import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "NER_entity_timeline_util",
        ['os', 'tkinter', 'pandas', 'numpy', 'matplotlib', 'stanza']) == False:
    sys.exit(0)

import os
import numpy as np
import pandas as pd
import tkinter.messagebox as mb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict

import IO_csv_util
import IO_files_util
import IO_user_interface_util


NER_COLORS = {
    'PERSON':  '#378ADD',
    'GPE':     '#E24B4A',
    'LOC':     '#639922',
    'ORG':     '#BA7517',
    'DATE':    '#534AB7',
    'EVENT':   '#D4537E',
    'NORP':    '#F9CB42',
    'FAC':     '#1D9E75',
}


def _extract_entities(filepath, nlp, doc_id):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if not text.strip():
        return []

    doc = nlp(text)
    rows = []
    total_sents = len(doc.sentences)

    for sent_idx, sent in enumerate(doc.sentences, 1):
        for ent in sent.ents:
            if ent.type in ('CARDINAL', 'ORDINAL', 'QUANTITY', 'PERCENT', 'MONEY', 'TIME'):
                continue
            rows.append({
                'Document ID': doc_id,
                'Document': os.path.basename(filepath),
                'Sentence ID': sent_idx,
                'Total Sentences': total_sents,
                'Narrative Position': round(sent_idx / total_sents, 4) if total_sents > 0 else 0,
                'Entity': ent.text.strip(),
                'Entity Type': ent.type,
                'Sentence': sent.text,
            })
    return rows


def plot_entity_timeline(df, entity_type, outputDir, base_name, top_n=10):
    type_df = df[df['Entity Type'] == entity_type]
    if len(type_df) == 0:
        return None

    entity_counts = type_df['Entity'].value_counts()
    top_entities = entity_counts.head(top_n).index.tolist()

    fig, ax = plt.subplots(figsize=(14, max(4, top_n * 0.5)))

    for i, entity in enumerate(top_entities):
        ent_df = type_df[type_df['Entity'] == entity]
        positions = ent_df['Narrative Position'].values
        ax.scatter(positions, [i] * len(positions), alpha=0.6, s=30,
                   color=NER_COLORS.get(entity_type, '#999999'),
                   edgecolors='white', linewidth=0.5)

    ax.set_yticks(range(len(top_entities)))
    ax.set_yticklabels(top_entities, fontsize=9)
    ax.set_xlabel('Narrative Position (0 = beginning, 1 = end)', fontsize=10)
    ax.set_xlim(-0.05, 1.05)
    ax.set_title(f'{entity_type} Entities — When They Appear ({base_name})', fontsize=12)
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()
    plt.tight_layout()

    out_file = os.path.join(outputDir, f'NER_timeline_{entity_type}.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    return out_file


def plot_entity_frequency(df, outputDir, base_name, top_n=20):
    entity_counts = df.groupby(['Entity', 'Entity Type']).size().reset_index(name='Count')
    entity_counts = entity_counts.nlargest(top_n, 'Count')

    if len(entity_counts) == 0:
        return None

    fig, ax = plt.subplots(figsize=(10, max(5, top_n * 0.35)))
    colors = [NER_COLORS.get(t, '#999999') for t in entity_counts['Entity Type']]
    labels = [f"{row['Entity']} ({row['Entity Type']})" for _, row in entity_counts.iterrows()]

    ax.barh(range(len(entity_counts)), entity_counts['Count'].values, color=colors, alpha=0.8)
    ax.set_yticks(range(len(entity_counts)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Frequency')
    ax.set_title(f'Top {top_n} Named Entities ({base_name})', fontsize=12)
    ax.grid(True, alpha=0.3, axis='x')

    unique_types = entity_counts['Entity Type'].unique()
    patches = [mpatches.Patch(color=NER_COLORS.get(t, '#999'), label=t) for t in unique_types]
    ax.legend(handles=patches, loc='lower right', fontsize=8)

    plt.tight_layout()
    out_file = os.path.join(outputDir, 'NER_frequency_chart.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    return out_file


def plot_entity_heatmap(df, outputDir, base_name, top_n=15, n_bins=10):
    entity_counts = df['Entity'].value_counts()
    top_entities = entity_counts.head(top_n).index.tolist()
    top_df = df[df['Entity'].isin(top_entities)]

    if len(top_df) == 0:
        return None

    bins = np.linspace(0, 1, n_bins + 1)
    bin_labels = [f'{bins[i]:.1f}-{bins[i+1]:.1f}' for i in range(n_bins)]

    matrix = np.zeros((len(top_entities), n_bins))
    for i, entity in enumerate(top_entities):
        positions = top_df[top_df['Entity'] == entity]['Narrative Position'].values
        hist, _ = np.histogram(positions, bins=bins)
        matrix[i] = hist

    fig, ax = plt.subplots(figsize=(12, max(5, len(top_entities) * 0.4)))
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
    ax.set_yticks(range(len(top_entities)))
    ax.set_yticklabels(top_entities, fontsize=8)
    ax.set_xticks(range(n_bins))
    ax.set_xticklabels(bin_labels, fontsize=7, rotation=45, ha='right')
    ax.set_xlabel('Narrative Position')
    ax.set_title(f'Entity Presence Heatmap ({base_name})', fontsize=12)
    plt.colorbar(im, ax=ax, shrink=0.8, label='Mentions')
    plt.tight_layout()

    out_file = os.path.join(outputDir, 'NER_entity_heatmap.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    return out_file


def main(inputFilename, inputDir, outputDir, chartPackage='Excel',
         dataTransformation='No transformation', top_n=10):

    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='NER_timeline', silent=True)
    if outputDir == '':
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running NER Entity Timeline at', True)

    import stanza
    try:
        nlp = stanza.Pipeline(lang='en', processors='tokenize,ner', use_gpu=False, logging_level='WARNING')
    except Exception as e:
        mb.showerror(title='Stanza Error',
                     message=f'Could not initialize Stanza NER pipeline.\n\n{str(e)}')
        return filesToOpen

    all_rows = []
    if inputFilename and os.path.exists(inputFilename):
        all_rows = _extract_entities(inputFilename, nlp, 1)
    elif inputDir and os.path.isdir(inputDir):
        doc_id = 0
        txt_files = sorted([f for f in os.listdir(inputDir) if f.endswith('.txt')])
        for filename in txt_files:
            doc_id += 1
            filepath = os.path.join(inputDir, filename)
            rows = _extract_entities(filepath, nlp, doc_id)
            all_rows.extend(rows)

    if not all_rows:
        mb.showwarning(title='No entities', message='No named entities found in the input text(s).')
        return filesToOpen

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'NER_entity_timeline',
                                                              '', '', '', '', False, True)

    df = pd.DataFrame(all_rows)
    df.to_csv(outputFilename, index=False, encoding='utf-8')
    filesToOpen.append(outputFilename)

    if inputFilename:
        base_name = os.path.basename(inputFilename)[:-4]
    else:
        base_name = os.path.basename(inputDir)

    freq_file = plot_entity_frequency(df, outputDir, base_name, top_n=20)
    if freq_file:
        filesToOpen.append(freq_file)

    for entity_type in ['PERSON', 'GPE', 'ORG', 'LOC']:
        type_df = df[df['Entity Type'] == entity_type]
        if len(type_df) >= 3:
            timeline_file = plot_entity_timeline(df, entity_type, outputDir, base_name, top_n=top_n)
            if timeline_file:
                filesToOpen.append(timeline_file)

    heatmap_file = plot_entity_heatmap(df, outputDir, base_name, top_n=15)
    if heatmap_file:
        filesToOpen.append(heatmap_file)

    # per-document entity counts
    if len(df['Document ID'].unique()) > 1:
        doc_entity_counts = df.groupby(['Document', 'Entity Type']).size().unstack(fill_value=0)
        doc_counts_file = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                                    '.csv', 'NER_per_document_counts',
                                                                    '', '', '', '', False, True)
        doc_entity_counts.to_csv(doc_counts_file, encoding='utf-8')
        filesToOpen.append(doc_counts_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                        'Finished running NER Entity Timeline at', True, '', True, startTime)

    return filesToOpen
