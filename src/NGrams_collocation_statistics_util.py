import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "NGrams_collocation_statistics_util",
        ['os', 'tkinter', 'pandas', 'numpy', 'nltk']) == False:
    sys.exit(0)

import os
import math
import numpy as np
import pandas as pd
import tkinter.messagebox as mb
from collections import Counter, defaultdict

import IO_csv_util
import IO_files_util
import IO_user_interface_util

from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text


def _tokenize_sentences(text):
    sentences = sentence_split_stanza_text(stanzaPipeLine(text))
    tokenized = []
    for s in sentences:
        words = [w.lower() for w in s.split() if w.isalpha() and len(w) > 1]
        if words:
            tokenized.append(words)
    return tokenized


def _compute_bigram_stats(sentences, min_freq=2, stop_words=None):
    if stop_words is None:
        try:
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
        except:
            stop_words = set()

    word_freq = Counter()
    bigram_freq = Counter()
    total_words = 0

    for sent in sentences:
        filtered = [w for w in sent if w not in stop_words]
        total_words += len(filtered)
        word_freq.update(filtered)
        for i in range(len(filtered) - 1):
            bigram_freq[(filtered[i], filtered[i + 1])] += 1

    results = []
    N = total_words

    for (w1, w2), freq in bigram_freq.items():
        if freq < min_freq:
            continue

        f_w1 = word_freq[w1]
        f_w2 = word_freq[w2]
        f_bigram = freq

        expected = (f_w1 * f_w2) / N if N > 0 else 0
        pmi = math.log2(f_bigram / expected) if expected > 0 and f_bigram > 0 else 0

        if expected > 0:
            ll_val = 2 * f_bigram * math.log(f_bigram / expected) if f_bigram > 0 else 0
        else:
            ll_val = 0

        a = f_bigram
        b = f_w1 - f_bigram
        c = f_w2 - f_bigram
        d = N - f_w1 - f_w2 + f_bigram
        chi2_num = N * (a * d - b * c) ** 2
        chi2_den = (a + b) * (c + d) * (a + c) * (b + d)
        chi2 = chi2_num / chi2_den if chi2_den > 0 else 0

        t_score = (f_bigram - expected) / math.sqrt(f_bigram) if f_bigram > 0 else 0

        dice = (2 * f_bigram) / (f_w1 + f_w2) if (f_w1 + f_w2) > 0 else 0

        results.append({
            'Word 1': w1,
            'Word 2': w2,
            'Bigram': f'{w1} {w2}',
            'Frequency': f_bigram,
            'Word 1 Freq': f_w1,
            'Word 2 Freq': f_w2,
            'PMI': round(pmi, 4),
            'Log-Likelihood': round(ll_val, 4),
            'Chi-Squared': round(chi2, 4),
            'T-Score': round(t_score, 4),
            'Dice Coefficient': round(dice, 4),
        })

    return results


def compute_collocation_statistics(inputFilename, inputDir, outputDir,
                                    chartPackage='Excel', dataTransformation='No transformation',
                                    min_freq=2, top_n=100):
    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='collocations', silent=True)
    if outputDir == '':
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running Collocation Statistics at', True)

    all_sentences = []

    if inputFilename and os.path.exists(inputFilename):
        with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        if text.strip():
            all_sentences.extend(_tokenize_sentences(text))
    elif inputDir and os.path.isdir(inputDir):
        txt_files = sorted([f for f in os.listdir(inputDir) if f.endswith('.txt')])
        for filename in txt_files:
            filepath = os.path.join(inputDir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            if text.strip():
                all_sentences.extend(_tokenize_sentences(text))

    if not all_sentences:
        mb.showwarning(title='No data', message='No text data found to analyze.')
        return filesToOpen

    results = _compute_bigram_stats(all_sentences, min_freq=min_freq)

    if not results:
        mb.showwarning(title='No collocations',
                       message=f'No bigrams found with minimum frequency of {min_freq}.')
        return filesToOpen

    df = pd.DataFrame(results)

    full_output = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                           '.csv', 'collocations_all',
                                                           '', '', '', '', False, True)
    df_sorted = df.sort_values('PMI', ascending=False)
    df_sorted.to_csv(full_output, index=False, encoding='utf-8')
    filesToOpen.append(full_output)

    for measure in ['PMI', 'Log-Likelihood', 'Chi-Squared', 'T-Score']:
        top_df = df.nlargest(top_n, measure)
        measure_file = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                                '.csv',
                                                                f'collocations_top_{measure.replace("-", "_")}',
                                                                '', '', '', '', False, True)
        top_df.to_csv(measure_file, index=False, encoding='utf-8')
        filesToOpen.append(measure_file)

    if chartPackage != 'No charts':
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        measures = ['PMI', 'Log-Likelihood', 'Chi-Squared', 'T-Score']
        colors = ['#378ADD', '#E24B4A', '#639922', '#BA7517']

        for ax, measure, color in zip(axes.flatten(), measures, colors):
            plot_df = df.nlargest(20, measure)
            ax.barh(range(len(plot_df)), plot_df[measure].values, color=color, alpha=0.8)
            ax.set_yticks(range(len(plot_df)))
            ax.set_yticklabels(plot_df['Bigram'].values, fontsize=8)
            ax.invert_yaxis()
            ax.set_title(f'Top 20 Collocations by {measure}', fontsize=11)
            ax.grid(True, alpha=0.3, axis='x')

        plt.suptitle('Collocation Statistics', fontsize=14)
        plt.tight_layout()

        chart_file = os.path.join(outputDir, 'collocation_statistics_chart.png')
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        filesToOpen.append(chart_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                        'Finished running Collocation Statistics at', True, '', True, startTime)

    return filesToOpen
