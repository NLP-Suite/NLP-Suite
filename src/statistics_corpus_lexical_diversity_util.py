import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "statistics_corpus_lexical_diversity_util",
        ['os', 'tkinter', 'pandas', 'numpy']) == False:
    sys.exit(0)

import os
import math
import numpy as np
import pandas as pd
import tkinter.messagebox as mb

import IO_csv_util
import IO_files_util
import IO_user_interface_util

from Stanza_functions_util import stanzaPipeLine, sentence_split_stanza_text


def _tokenize(text):
    sentences = sentence_split_stanza_text(stanzaPipeLine(text))
    words = []
    for s in sentences:
        words.extend(s.lower().split())
    words = [w for w in words if w.isalpha()]
    return words


def _ttr(tokens):
    if len(tokens) == 0:
        return 0.0
    return len(set(tokens)) / len(tokens)


def _root_ttr(tokens):
    if len(tokens) == 0:
        return 0.0
    return len(set(tokens)) / math.sqrt(len(tokens))


def _log_ttr(tokens):
    if len(tokens) < 2:
        return 0.0
    return math.log(len(set(tokens))) / math.log(len(tokens))


def _mtld_forward(tokens, threshold=0.72):
    factor_count = 0.0
    start = 0
    for i in range(1, len(tokens) + 1):
        segment = tokens[start:i]
        current_ttr = _ttr(segment)
        if current_ttr <= threshold:
            factor_count += 1
            start = i
    if start < len(tokens):
        remaining = tokens[start:]
        if len(remaining) > 0:
            remaining_ttr = _ttr(remaining)
            if remaining_ttr < 1.0:
                factor_count += (1.0 - remaining_ttr) / (1.0 - threshold)
    if factor_count == 0:
        return len(tokens)
    return len(tokens) / factor_count


def _mtld(tokens, threshold=0.72):
    if len(tokens) < 10:
        return 0.0
    forward = _mtld_forward(tokens, threshold)
    backward = _mtld_forward(tokens[::-1], threshold)
    return (forward + backward) / 2.0


def _vocd_single(tokens, sample_size):
    if sample_size > len(tokens):
        return _ttr(tokens)
    indices = np.random.choice(len(tokens), sample_size, replace=False)
    sample = [tokens[i] for i in indices]
    return _ttr(sample)


def _vocd(tokens, n_trials=100, min_sample=35, max_sample=50):
    if len(tokens) < min_sample:
        return 0.0
    actual_max = min(max_sample, len(tokens))
    sample_sizes = list(range(min_sample, actual_max + 1))
    if not sample_sizes:
        return 0.0

    observed_ttrs = {}
    for ss in sample_sizes:
        ttrs = [_vocd_single(tokens, ss) for _ in range(n_trials)]
        observed_ttrs[ss] = np.mean(ttrs)

    best_d = 50.0
    best_err = float('inf')
    for d_candidate in np.arange(10, 200, 0.5):
        err = 0
        for ss in sample_sizes:
            if d_candidate == 0:
                expected = 1.0
            else:
                expected = (d_candidate / ss) * (math.sqrt(1 + 2 * ss / d_candidate) - 1)
            err += (observed_ttrs[ss] - expected) ** 2
        if err < best_err:
            best_err = err
            best_d = d_candidate

    return best_d


def compute_lexical_diversity(inputFilename, inputDir, outputDir,
                               chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='lexical_diversity', silent=True)
    if outputDir == '':
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running Lexical Diversity analysis at', True)

    files_to_process = []
    if inputFilename and os.path.exists(inputFilename):
        files_to_process.append(inputFilename)
    elif inputDir and os.path.isdir(inputDir):
        files_to_process = [os.path.join(inputDir, f) for f in sorted(os.listdir(inputDir))
                            if f.endswith('.txt')]

    if not files_to_process:
        mb.showwarning(title='No data', message='No text files found to analyze.')
        return filesToOpen

    rows = []
    for filepath in files_to_process:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        if not text.strip():
            continue

        tokens = _tokenize(text)
        if len(tokens) < 10:
            continue

        doc_name = os.path.basename(filepath)

        row = {
            'Document': doc_name,
            'Total Tokens': len(tokens),
            'Unique Types': len(set(tokens)),
            'TTR': round(_ttr(tokens), 4),
            'Root TTR (Guiraud)': round(_root_ttr(tokens), 4),
            'Log TTR (Herdan)': round(_log_ttr(tokens), 4),
            'MTLD': round(_mtld(tokens), 2),
            'vocd-D': round(_vocd(tokens), 2),
        }
        rows.append(row)

    if not rows:
        mb.showwarning(title='No data',
                       message='No documents with sufficient text to analyze (minimum 10 words).')
        return filesToOpen

    df = pd.DataFrame(rows)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'lexical_diversity',
                                                              '', '', '', '', False, True)
    df.to_csv(outputFilename, index=False, encoding='utf-8')
    filesToOpen.append(outputFilename)

    if len(df) > 1 and chartPackage != 'No charts':
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        measures = [('TTR', 'Type-Token Ratio'),
                    ('Root TTR (Guiraud)', 'Root TTR (Guiraud Index)'),
                    ('MTLD', 'Measure of Textual Lexical Diversity'),
                    ('vocd-D', 'vocd-D (vocabulary diversity)')]

        for ax, (col, title) in zip(axes.flatten(), measures):
            values = df[col].values
            short_names = [n[:15] for n in df['Document'].values]
            ax.barh(range(len(values)), values, color='#378ADD', alpha=0.8)
            ax.set_yticks(range(len(values)))
            ax.set_yticklabels(short_names, fontsize=7)
            ax.invert_yaxis()
            ax.set_title(title, fontsize=11)
            ax.grid(True, alpha=0.3, axis='x')

        plt.suptitle('Lexical Diversity Measures', fontsize=14, y=1.01)
        plt.tight_layout()

        chart_file = os.path.join(outputDir, 'lexical_diversity_chart.png')
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        filesToOpen.append(chart_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                        'Finished running Lexical Diversity analysis at', True, '', True, startTime)

    return filesToOpen
