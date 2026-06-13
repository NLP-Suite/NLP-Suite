import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "statistics_corpus_readability_util",
        ['os', 'tkinter', 'pandas', 'numpy', 're']) == False:
    sys.exit(0)

import os
import re
import numpy as np
import pandas as pd
import tkinter.messagebox as mb

import IO_csv_util
import IO_files_util
import IO_user_interface_util


def _count_syllables(word):
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:es|ed|e)$', '', word) or word
    vowels = re.findall(r'[aeiouy]+', word)
    return max(1, len(vowels))


def _analyze_text(text):
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    n_sentences = max(1, len(sentences))

    words = re.findall(r"[a-zA-Z']+", text)
    n_words = max(1, len(words))

    syllable_counts = [_count_syllables(w) for w in words]
    n_syllables = sum(syllable_counts)
    n_polysyllabic = sum(1 for c in syllable_counts if c >= 3)

    char_counts = [len(w) for w in words]
    n_chars = sum(char_counts)

    return n_sentences, n_words, n_syllables, n_polysyllabic, n_chars


def _flesch_reading_ease(n_sentences, n_words, n_syllables):
    return 206.835 - 1.015 * (n_words / n_sentences) - 84.6 * (n_syllables / n_words)


def _flesch_kincaid_grade(n_sentences, n_words, n_syllables):
    return 0.39 * (n_words / n_sentences) + 11.8 * (n_syllables / n_words) - 15.59


def _gunning_fog(n_sentences, n_words, n_polysyllabic):
    return 0.4 * ((n_words / n_sentences) + 100 * (n_polysyllabic / n_words))


def _coleman_liau(n_sentences, n_words, n_chars):
    L = (n_chars / n_words) * 100
    S = (n_sentences / n_words) * 100
    return 0.0588 * L - 0.296 * S - 15.8


def _ari(n_sentences, n_words, n_chars):
    return 4.71 * (n_chars / n_words) + 0.5 * (n_words / n_sentences) - 21.43


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def _interpret_fre(score):
    if score >= 90:
        return "Very Easy (5th grade)"
    elif score >= 80:
        return "Easy (6th grade)"
    elif score >= 70:
        return "Fairly Easy (7th grade)"
    elif score >= 60:
        return "Standard (8th-9th grade)"
    elif score >= 50:
        return "Fairly Difficult (10th-12th grade)"
    elif score >= 30:
        return "Difficult (College)"
    else:
        return "Very Difficult (Graduate)"


def compute_readability(inputFilename, inputDir, outputDir, chartPackage='Excel',
                         dataTransformation='No transformation'):
    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='readability', silent=True)
    if outputDir == '':
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running Readability Analysis at', True)

    rows = []
    if inputFilename and os.path.exists(inputFilename):
        with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        if text.strip():
            n_sent, n_words, n_syll, n_poly, n_chars = _analyze_text(text)
            rows.append({
                'Document': os.path.basename(inputFilename),
                'Sentences': n_sent,
                'Words': n_words,
                'Syllables': n_syll,
                'Polysyllabic Words': n_poly,
                'Characters': n_chars,
                'Flesch Reading Ease': round(_clamp(_flesch_reading_ease(n_sent, n_words, n_syll), 0, 121), 2),
                'Flesch-Kincaid Grade': round(_clamp(_flesch_kincaid_grade(n_sent, n_words, n_syll), 0, 30), 2),
                'Gunning Fog Index': round(_clamp(_gunning_fog(n_sent, n_words, n_poly), 0, 30), 2),
                'Coleman-Liau Index': round(_clamp(_coleman_liau(n_sent, n_words, n_chars), 0, 30), 2),
                'Automated Readability Index': round(_clamp(_ari(n_sent, n_words, n_chars), 0, 30), 2),
            })
    elif inputDir and os.path.isdir(inputDir):
        txt_files = sorted([f for f in os.listdir(inputDir) if f.endswith('.txt')])
        for filename in txt_files:
            filepath = os.path.join(inputDir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            if not text.strip():
                continue
            n_sent, n_words, n_syll, n_poly, n_chars = _analyze_text(text)
            rows.append({
                'Document': filename,
                'Sentences': n_sent,
                'Words': n_words,
                'Syllables': n_syll,
                'Polysyllabic Words': n_poly,
                'Characters': n_chars,
                'Flesch Reading Ease': round(_clamp(_flesch_reading_ease(n_sent, n_words, n_syll), 0, 121), 2),
                'Flesch-Kincaid Grade': round(_clamp(_flesch_kincaid_grade(n_sent, n_words, n_syll), 0, 30), 2),
                'Gunning Fog Index': round(_clamp(_gunning_fog(n_sent, n_words, n_poly), 0, 30), 2),
                'Coleman-Liau Index': round(_clamp(_coleman_liau(n_sent, n_words, n_chars), 0, 30), 2),
                'Automated Readability Index': round(_clamp(_ari(n_sent, n_words, n_chars), 0, 30), 2),
            })

    if not rows:
        mb.showwarning(title='No data', message='No text data found to analyze.')
        return filesToOpen

    df = pd.DataFrame(rows)
    df['Interpretation'] = df['Flesch Reading Ease'].apply(_interpret_fre)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'readability_scores',
                                                              '', '', '', '', False, True)
    df.to_csv(outputFilename, index=False, encoding='utf-8')
    filesToOpen.append(outputFilename)

    if chartPackage != 'No charts' and len(df) > 0:
        import matplotlib.pyplot as plt

        measures = ['Flesch Reading Ease', 'Flesch-Kincaid Grade', 'Gunning Fog Index',
                     'Coleman-Liau Index', 'Automated Readability Index']
        colors = ['#378ADD', '#E24B4A', '#639922', '#BA7517', '#534AB7']

        if len(df) == 1:
            fig, ax = plt.subplots(figsize=(10, 5))
            values = [df[m].values[0] for m in measures]
            ax.barh(range(len(measures)), values, color=colors, alpha=0.8)
            ax.set_yticks(range(len(measures)))
            ax.set_yticklabels(measures, fontsize=9)
            ax.set_xlabel('Score')
            ax.set_title(f'Readability Scores — {df["Document"].values[0]}', fontsize=12)
            ax.grid(True, alpha=0.3, axis='x')
            ax.invert_yaxis()
            plt.tight_layout()
        else:
            fig, axes = plt.subplots(2, 3, figsize=(18, 10))
            axes = axes.flatten()

            for idx, (measure, color) in enumerate(zip(measures, colors)):
                ax = axes[idx]
                doc_labels = [d[:30] for d in df['Document'].values]
                vals = df[measure].values
                ax.barh(range(len(vals)), vals, color=color, alpha=0.8)
                ax.set_yticks(range(len(vals)))
                ax.set_yticklabels(doc_labels, fontsize=7)
                ax.invert_yaxis()
                ax.set_title(measure, fontsize=10)
                ax.grid(True, alpha=0.3, axis='x')

            axes[-1].axis('off')
            plt.suptitle('Readability Scores by Document', fontsize=13)
            plt.tight_layout()

        chart_file = os.path.join(outputDir, 'readability_scores_chart.png')
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        filesToOpen.append(chart_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                        'Finished running Readability Analysis at', True, '', True, startTime)

    return filesToOpen
