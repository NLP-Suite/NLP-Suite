import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "statistics_corpus_tfidf_util",
        ['os', 'tkinter', 'pandas', 'sklearn']) == False:
    sys.exit(0)

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

import IO_csv_util
import IO_files_util
import IO_user_interface_util
import charts_util


def compute_tfidf(inputFilename, inputDir, outputDir, chartPackage='Excel',
                  dataTransformation='No transformation', max_features=50,
                  stop_words='english'):
    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='TF-IDF', silent=True)
    if outputDir == '':
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running TF-IDF analysis at', True)

    documents = []
    doc_names = []

    if inputFilename and os.path.exists(inputFilename):
        with open(inputFilename, 'r', encoding='utf-8', errors='ignore') as f:
            documents.append(f.read())
        doc_names.append(os.path.basename(inputFilename))
    elif inputDir and os.path.isdir(inputDir):
        txt_files = sorted([f for f in os.listdir(inputDir) if f.endswith('.txt')])
        for filename in txt_files:
            filepath = os.path.join(inputDir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            if text.strip():
                documents.append(text)
                doc_names.append(filename)

    if len(documents) == 0:
        import tkinter.messagebox as mb
        mb.showwarning(title='No data', message='No text files found to analyze.')
        return filesToOpen

    vectorizer = TfidfVectorizer(max_features=max_features, stop_words=stop_words,
                                  sublinear_tf=True)
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()

    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names,
                             index=doc_names)
    tfidf_df.index.name = 'Document'

    full_output = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                           '.csv', 'TF-IDF_matrix',
                                                           '', '', '', '', False, True)
    tfidf_df.to_csv(full_output, encoding='utf-8')
    filesToOpen.append(full_output)

    top_words_rows = []
    for i, doc in enumerate(doc_names):
        scores = tfidf_matrix[i].toarray().flatten()
        top_indices = scores.argsort()[::-1][:20]
        for rank, idx in enumerate(top_indices, 1):
            if scores[idx] > 0:
                top_words_rows.append({
                    'Document': doc,
                    'Rank': rank,
                    'Word': feature_names[idx],
                    'TF-IDF Score': round(scores[idx], 4)
                })

    top_df = pd.DataFrame(top_words_rows)
    top_output = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                          '.csv', 'TF-IDF_top_words',
                                                          '', '', '', '', False, True)
    top_df.to_csv(top_output, index=False, encoding='utf-8')
    filesToOpen.append(top_output)

    if len(documents) > 1 and chartPackage != 'No charts':
        import matplotlib.pyplot as plt

        mean_scores = tfidf_matrix.toarray().mean(axis=0)
        top_corpus_idx = mean_scores.argsort()[::-1][:20]
        top_words = [feature_names[i] for i in top_corpus_idx]
        top_scores = [mean_scores[i] for i in top_corpus_idx]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(top_words)), top_scores, color='#378ADD')
        ax.set_yticks(range(len(top_words)))
        ax.set_yticklabels(top_words, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Mean TF-IDF Score')
        ax.set_title('Top 20 Most Distinctive Words Across Corpus')
        plt.tight_layout()

        chart_file = os.path.join(outputDir, 'TF-IDF_top_words_chart.png')
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        filesToOpen.append(chart_file)

    if len(documents) > 1:
        from sklearn.metrics.pairwise import cosine_similarity
        import matplotlib.pyplot as plt

        sim_matrix = cosine_similarity(tfidf_matrix)
        sim_df = pd.DataFrame(sim_matrix, index=doc_names, columns=doc_names)

        sim_output = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'TF-IDF_similarity',
                                                              '', '', '', '', False, True)
        sim_df.to_csv(sim_output, encoding='utf-8')
        filesToOpen.append(sim_output)

        if len(documents) <= 50:
            fig, ax = plt.subplots(figsize=(max(8, len(documents) * 0.5),
                                             max(6, len(documents) * 0.4)))
            im = ax.imshow(sim_matrix, cmap='YlOrRd', vmin=0, vmax=1)
            ax.set_xticks(range(len(doc_names)))
            ax.set_yticks(range(len(doc_names)))
            short_names = [n[:20] for n in doc_names]
            ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=7)
            ax.set_yticklabels(short_names, fontsize=7)
            ax.set_title('Document Similarity (TF-IDF Cosine)')
            plt.colorbar(im, ax=ax, shrink=0.8)
            plt.tight_layout()

            heatmap_file = os.path.join(outputDir, 'TF-IDF_similarity_heatmap.png')
            plt.savefig(heatmap_file, dpi=150, bbox_inches='tight')
            plt.close()
            filesToOpen.append(heatmap_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                        'Finished running TF-IDF analysis at', True, '', True, startTime)

    return filesToOpen
