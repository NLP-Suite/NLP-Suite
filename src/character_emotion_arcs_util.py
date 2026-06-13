import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "character_emotion_arcs_util",
        ['os', 'csv', 'tkinter', 'nrclex', 'numpy', 'matplotlib', 'pandas', 'stanza']) == False:
    sys.exit(0)

import os
import csv
import math
import numpy as np
import pandas as pd
import tkinter.messagebox as mb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict
from nrclex import NRCLex

import IO_csv_util
import IO_files_util
import IO_user_interface_util
import charts_util

EIGHT_EMOTIONS = ["anger", "anticipation", "disgust", "fear",
                   "joy", "sadness", "surprise", "trust"]

NRC_COLORS = {
    "anger":        "#E24B4A",
    "anticipation": "#BA7517",
    "disgust":      "#D4537E",
    "fear":         "#1D9E75",
    "joy":          "#F9CB42",
    "sadness":      "#534AB7",
    "surprise":     "#378ADD",
    "trust":        "#639922",
}


def _score_sentence_nrc(text):
    emotion_obj = NRCLex(text)
    raw = emotion_obj.raw_emotion_scores
    total = sum(raw.get(e, 0) for e in EIGHT_EMOTIONS) or 1
    return {e: raw.get(e, 0) / total for e in EIGHT_EMOTIONS}


def _extract_persons_from_sentence(sent):
    persons = set()
    for ent in sent.ents:
        if ent.type == "PERSON":
            persons.add(ent.text.strip())
    return persons


def _normalize_character_name(name, canonical_map):
    lower = name.lower()
    if lower in canonical_map:
        return canonical_map[lower]
    for canon_lower, canon in canonical_map.items():
        if lower in canon_lower or canon_lower in lower:
            canonical_map[lower] = canon
            return canon
    canonical_map[lower] = name
    return name


def analyze_file(filepath, nlp_pipeline, doc_id):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if not text.strip():
        return []

    doc = nlp_pipeline(text)
    canonical_map = {}
    rows = []

    for sent_idx, sent in enumerate(doc.sentences, 1):
        sent_text = sent.text
        persons = _extract_persons_from_sentence(sent)
        scores = _score_sentence_nrc(sent_text)

        normalized_persons = set()
        for p in persons:
            normalized_persons.add(_normalize_character_name(p, canonical_map))

        if not normalized_persons:
            normalized_persons = {"_NARRATOR/UNATTRIBUTED_"}

        for character in normalized_persons:
            row = {
                'Document ID': doc_id,
                'Document': IO_csv_util.dressFilenameForCSVHyperlink(filepath),
                'Sentence ID': sent_idx,
                'Sentence': sent_text,
                'Character': character,
            }
            for e in EIGHT_EMOTIONS:
                row[e.capitalize()] = round(scores[e], 4)
            rows.append(row)

    return rows


def plot_character_arcs(df, character, outputDir, base_name, window_size=5):
    char_df = df[df['Character'] == character].copy()
    char_df = char_df.sort_values('Sentence ID').reset_index(drop=True)

    if len(char_df) < 2:
        return []

    files = []
    fig, ax = plt.subplots(figsize=(12, 6))

    for emotion in EIGHT_EMOTIONS:
        col = emotion.capitalize()
        values = char_df[col].values
        if window_size > 1 and len(values) >= window_size:
            smoothed = pd.Series(values).rolling(window=window_size, center=True, min_periods=1).mean().values
        else:
            smoothed = values
        ax.plot(range(len(smoothed)), smoothed, label=emotion.capitalize(),
                color=NRC_COLORS[emotion], linewidth=1.8, alpha=0.85)

    ax.set_xlabel('Narrative Position (sentence)', fontsize=11)
    ax.set_ylabel('Emotion Intensity', fontsize=11)
    safe_char = character.replace('/', '_').replace('\\', '_').replace(' ', '_')[:30]
    ax.set_title(f'Emotion Arc — {character}\n({base_name})', fontsize=13)
    ax.legend(loc='upper right', fontsize=8, ncol=2)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    arc_file = os.path.join(outputDir, f'emotion_arc_{safe_char}.png')
    plt.savefig(arc_file, dpi=150, bbox_inches='tight')
    plt.close()
    files.append(arc_file)

    return files


def plot_character_comparison(df, characters, emotion, outputDir, base_name, window_size=5):
    fig, ax = plt.subplots(figsize=(12, 5))
    col = emotion.capitalize()
    colors = plt.cm.tab10.colors

    for i, character in enumerate(characters):
        char_df = df[df['Character'] == character].sort_values('Sentence ID')
        if len(char_df) < 2:
            continue
        values = char_df[col].values
        if window_size > 1 and len(values) >= window_size:
            smoothed = pd.Series(values).rolling(window=window_size, center=True, min_periods=1).mean().values
        else:
            smoothed = values
        ax.plot(range(len(smoothed)), smoothed, label=character,
                color=colors[i % len(colors)], linewidth=1.8)

    ax.set_xlabel('Narrative Position (sentence)', fontsize=11)
    ax.set_ylabel(f'{col} Intensity', fontsize=11)
    ax.set_title(f'{col} Arc — Character Comparison\n({base_name})', fontsize=13)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    safe_emo = emotion.replace(' ', '_')
    out_file = os.path.join(outputDir, f'character_comparison_{safe_emo}.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    return out_file


def plot_dominant_emotion_timeline(df, character, outputDir, base_name):
    char_df = df[df['Character'] == character].sort_values('Sentence ID').reset_index(drop=True)
    if len(char_df) < 2:
        return None

    emotion_cols = [e.capitalize() for e in EIGHT_EMOTIONS]
    dominant = char_df[emotion_cols].idxmax(axis=1)

    fig, ax = plt.subplots(figsize=(14, 3))
    color_map = {e.capitalize(): NRC_COLORS[e] for e in EIGHT_EMOTIONS}

    for i, emo in enumerate(dominant):
        ax.barh(0, 1, left=i, color=color_map.get(emo, '#999999'), edgecolor='none')

    ax.set_xlim(0, len(dominant))
    ax.set_yticks([])
    ax.set_xlabel('Narrative Position (sentence)', fontsize=10)
    safe_char = character.replace('/', '_').replace('\\', '_').replace(' ', '_')[:30]
    ax.set_title(f'Dominant Emotion Timeline — {character} ({base_name})', fontsize=12)

    patches = [mpatches.Patch(color=NRC_COLORS[e], label=e.capitalize()) for e in EIGHT_EMOTIONS]
    ax.legend(handles=patches, loc='upper center', bbox_to_anchor=(0.5, -0.25),
              ncol=4, fontsize=8)

    plt.tight_layout()
    out_file = os.path.join(outputDir, f'dominant_emotion_timeline_{safe_char}.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    return out_file


def main(inputFilename, inputDir, outputDir, chartPackage='Excel',
         dataTransformation='No transformation', min_sentences=5, top_n_characters=5,
         window_size=5):

    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='character_emotion_arcs', silent=True)
    if outputDir == '':
        return filesToOpen

    import stanza
    try:
        nlp = stanza.Pipeline(lang='en', processors='tokenize,ner', use_gpu=False)
    except Exception as e:
        mb.showerror(title='Stanza Error',
                     message=f'Could not initialize Stanza NER pipeline.\n\n{str(e)}')
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running Character Emotion Arcs at', True)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'character_emotion_arcs',
                                                              '', '', '', '', False, True)

    fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Character'] + \
                 [e.capitalize() for e in EIGHT_EMOTIONS]

    all_rows = []
    if inputFilename and os.path.exists(inputFilename):
        all_rows = analyze_file(inputFilename, nlp, 1)
    elif inputDir and os.path.isdir(inputDir):
        doc_id = 0
        txt_files = sorted([f for f in os.listdir(inputDir) if f.endswith('.txt')])
        for file in txt_files:
            doc_id += 1
            filepath = os.path.join(inputDir, file)
            rows = analyze_file(filepath, nlp, doc_id)
            all_rows.extend(rows)

    if not all_rows:
        mb.showwarning(title='No data', message='No text data found to analyze.')
        return filesToOpen

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    filesToOpen.append(outputFilename)

    df = pd.read_csv(outputFilename)

    named_chars = df[df['Character'] != '_NARRATOR/UNATTRIBUTED_']
    char_counts = named_chars.groupby('Character')['Sentence ID'].count()
    eligible = char_counts[char_counts >= min_sentences]
    top_characters = eligible.nlargest(top_n_characters).index.tolist()

    if inputFilename:
        base_name = os.path.basename(inputFilename)[:-4]
    else:
        base_name = os.path.basename(inputDir)

    for character in top_characters:
        arc_files = plot_character_arcs(df, character, outputDir, base_name, window_size)
        filesToOpen.extend(arc_files)

        timeline_file = plot_dominant_emotion_timeline(df, character, outputDir, base_name)
        if timeline_file:
            filesToOpen.append(timeline_file)

    if len(top_characters) >= 2:
        for emotion in ['joy', 'anger', 'fear', 'sadness']:
            comp_file = plot_character_comparison(df, top_characters, emotion, outputDir,
                                                   base_name, window_size)
            filesToOpen.append(comp_file)

    summary_file = os.path.join(outputDir, f'character_emotion_summary_{base_name}.csv')
    summary_rows = []
    for character in top_characters:
        char_df = df[df['Character'] == character]
        row = {'Character': character, 'Sentences': len(char_df)}
        for e in EIGHT_EMOTIONS:
            row[f'Avg {e.capitalize()}'] = round(char_df[e.capitalize()].mean(), 4)
        emotion_cols = [e.capitalize() for e in EIGHT_EMOTIONS]
        avg_vals = {e: char_df[e].mean() for e in emotion_cols}
        row['Dominant Emotion'] = max(avg_vals, key=avg_vals.get)
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(summary_file, index=False, encoding='utf-8')
    filesToOpen.append(summary_file)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                        'Finished running Character Emotion Arcs at', True, '', True, startTime)

    return filesToOpen
