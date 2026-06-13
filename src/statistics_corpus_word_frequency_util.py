import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "statistics_corpus_word_frequency_util",
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


def compute_word_frequency(inputFilename, inputDir, outputDir, chartPackage='Excel',
                            dataTransformation='No transformation', top_n=50):

    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='word_frequency', silent=True)
    if outputDir == '':
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running Word Frequency Distribution at', True)

    all_words = []
    if inputFilename and os.path.exists(inputFilename):
        with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        words = re.findall(r"[a-zA-Z']+", text.lower())
        all_words.extend(words)
    elif inputDir and os.path.isdir(inputDir):
        txt_files = sorted([f for f in os.listdir(inputDir) if f.endswith('.txt')])
        for filename in txt_files:
            filepath = os.path.join(inputDir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            words = re.findall(r"[a-zA-Z']+", text.lower())
            all_words.extend(words)

    if not all_words:
        mb.showwarning(title='No data', message='No text data found to analyze.')
        return filesToOpen

    from collections import Counter
    word_counts = Counter(all_words)

    rows = []
    for rank, (word, freq) in enumerate(word_counts.most_common(), 1):
        rows.append({
            'Rank': rank,
            'Word': word,
            'Frequency': freq,
            'Log Rank': round(np.log10(rank), 4) if rank > 0 else 0,
            'Log Frequency': round(np.log10(freq), 4) if freq > 0 else 0,
        })

    df = pd.DataFrame(rows)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'word_frequency_distribution',
                                                              '', '', '', '', False, True)
    df.to_csv(outputFilename, index=False, encoding='utf-8')
    filesToOpen.append(outputFilename)

    if chartPackage != 'No charts':
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(20, 6))

        # 1. Top N words bar chart
        top_df = df.head(top_n)
        axes[0].barh(range(len(top_df)), top_df['Frequency'].values, color='#378ADD', alpha=0.8)
        axes[0].set_yticks(range(len(top_df)))
        axes[0].set_yticklabels(top_df['Word'].values, fontsize=7)
        axes[0].invert_yaxis()
        axes[0].set_xlabel('Frequency')
        axes[0].set_title(f'Top {top_n} Most Frequent Words', fontsize=11)
        axes[0].grid(True, alpha=0.3, axis='x')

        # 2. Zipf's Law: log-log rank-frequency plot
        axes[1].scatter(df['Log Rank'].values, df['Log Frequency'].values,
                        s=3, alpha=0.4, color='#E24B4A')
        max_rank = df['Log Rank'].max()
        max_freq = df['Log Frequency'].max()
        ideal_x = np.linspace(0, max_rank, 100)
        ideal_y = max_freq - ideal_x
        axes[1].plot(ideal_x, ideal_y, '--', color='#333333', alpha=0.6, linewidth=1.5,
                     label="Zipf's ideal (slope = -1)")
        axes[1].set_xlabel('Log₁₀(Rank)')
        axes[1].set_ylabel('Log₁₀(Frequency)')
        axes[1].set_title("Zipf's Law — Rank vs. Frequency (log-log)", fontsize=11)
        axes[1].legend(fontsize=8)
        axes[1].grid(True, alpha=0.3)

        # 3. Cumulative frequency
        total = df['Frequency'].sum()
        cumulative = np.cumsum(df['Frequency'].values) / total * 100
        axes[2].plot(range(1, len(cumulative) + 1), cumulative, color='#639922', linewidth=1.5)
        n50 = np.searchsorted(cumulative, 50) + 1
        n90 = np.searchsorted(cumulative, 90) + 1
        axes[2].axhline(y=50, color='#BA7517', linestyle='--', alpha=0.5)
        axes[2].axhline(y=90, color='#BA7517', linestyle='--', alpha=0.5)
        axes[2].annotate(f'{n50} words = 50%', xy=(n50, 50), fontsize=8,
                         xytext=(n50 + len(df) * 0.05, 45))
        axes[2].annotate(f'{n90} words = 90%', xy=(n90, 90), fontsize=8,
                         xytext=(n90 + len(df) * 0.05, 85))
        axes[2].set_xlabel('Number of Unique Words (ranked)')
        axes[2].set_ylabel('Cumulative % of Total Words')
        axes[2].set_title('Cumulative Word Coverage', fontsize=11)
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        chart_file = os.path.join(outputDir, 'word_frequency_distribution_chart.png')
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        filesToOpen.append(chart_file)

        # Hapax legomena summary
        hapax = df[df['Frequency'] == 1]
        n_hapax = len(hapax)
        n_total_types = len(df)
        hapax_pct = round(100 * n_hapax / n_total_types, 1) if n_total_types > 0 else 0
        summary = pd.DataFrame([{
            'Total Tokens': total,
            'Total Types (unique words)': n_total_types,
            'Hapax Legomena (freq=1)': n_hapax,
            'Hapax % of Types': hapax_pct,
            'Words for 50% Coverage': n50,
            'Words for 90% Coverage': n90,
        }])
        summary_file = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                                '.csv', 'word_frequency_summary',
                                                                '', '', '', '', False, True)
        summary.to_csv(summary_file, index=False, encoding='utf-8')
        filesToOpen.append(summary_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                        'Finished running Word Frequency Distribution at', True, '', True, startTime)

    return filesToOpen
