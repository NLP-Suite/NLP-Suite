import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "character_emotion_arcs_util",
        ['os', 'csv', 'tkinter', 'nrclex', 'numpy', 'matplotlib', 'pandas', 'stanza']) == False:
    sys.exit(0)

import os
import csv
import re
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
    # NRCLex API drift: older versions expose .raw_emotion_scores (counts); some newer builds only
    # populate .affect_frequencies (normalized). Fall back so a version mismatch doesn't crash the
    # character emotion arcs -- either is fine here since we re-normalize over the 8 emotions below.
    raw = getattr(emotion_obj, 'raw_emotion_scores', None)
    if not raw:
        raw = getattr(emotion_obj, 'affect_frequencies', None) or {}
    total = sum(raw.get(e, 0) for e in EIGHT_EMOTIONS) or 1
    return {e: raw.get(e, 0) / total for e in EIGHT_EMOTIONS}


def _extract_persons_from_sentence(sent):
    persons = set()
    for ent in sent.ents:
        if ent.type == "PERSON":
            persons.add(ent.text.strip())
    return persons


def _strip_possessive(name):
    """"Harry's" and "Harrys" are Harry. NER hands back the possessive form of a
    name often enough that leaving it alone produced a separate character with
    1,890 sentences of its own in the Harry Potter corpus."""
    name = name.strip()
    for suffix in ("’s", "'s", "’", "'"):
        if name.endswith(suffix) and len(name) > len(suffix) + 1:
            return name[:-len(suffix)].strip()
    if len(name) > 2 and name.endswith('s') and not name.endswith('ss'):
        return name          # 'Harrys' -> left alone here; the map below folds it in
    return name


# Words that are not part of a name, and must not be what two names are matched on.
_TITLES = {'mr', 'mrs', 'ms', 'miss', 'dr', 'doctor', 'professor', 'prof', 'sir',
           'lady', 'lord', 'madam', 'madame', 'uncle', 'aunt', 'auntie', 'the',
           'a', 'an', 'of', 'and'}


def _name_tokens(name):
    """The words of a name that identify a person: no titles, no punctuation."""
    cleaned = re.sub(r"[^\w\s]", ' ', name.lower())
    return {w for w in cleaned.split() if w and w not in _TITLES}


def _normalize_character_name(name, canonical_map):
    """Fold a name into the one already seen for that person.

    Matching is on WORDS, and only when one name's words are all contained in
    the other's: "Harry" and "Mr. Potter" both fold into "Harry Potter". It used
    to be a raw substring test, which is a different thing entirely - "ron" is
    inside "the leaky cauld-RON", and "gran" inside "hermione GRAN-ger", so Ron
    and Hermione were absorbed into a pub and a grandmother.

    A name that could belong to two different people already seen is left alone.
    Uniqueness is the safeguard: guessing which character a mention belongs to
    would be worse than reporting them separately, and the CSV shows the split.

    *canonical_map* is shared by the WHOLE corpus. Rebuilt per document, each of
    199 Harry Potter files chose its own canonical form, so one person came out
    as Harry, Harry's, Harry Potter, Harrys and The Cave Harry.
    """
    name = _strip_possessive(name)
    lower = name.lower().strip()
    if not lower:
        return name
    # every entry is (the name to use, the tokens of THAT name) - an alias keeps
    # its canonical form's tokens, so aliases never widen what will match next
    if lower in canonical_map:
        return canonical_map[lower][0]

    tokens = _name_tokens(name)
    if tokens:
        candidates = {}
        for canon, canon_tokens in canonical_map.values():
            if canon_tokens and (tokens <= canon_tokens or canon_tokens <= tokens):
                candidates[canon] = canon_tokens
        if len(candidates) == 1:
            canon, canon_tokens = next(iter(candidates.items()))
            canonical_map[lower] = (canon, canon_tokens)
            return canon

    canonical_map[lower] = (name, tokens)
    return name


def analyze_file(filepath, nlp_pipeline, doc_id, canonical_map=None):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if not text.strip():
        return []

    doc = nlp_pipeline(text)
    # one map for the whole corpus when the caller keeps it; see
    # _normalize_character_name for why per-document maps split people up
    if canonical_map is None:
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


def analyze_conll_table(conll_path):
    """Same output as analyze_file, but DERIVED from an existing Stanza NER CoNLL table (Form + NER +
    Sentence ID + Document ID, one token per row) instead of re-parsing the corpus with Stanza NER. The
    Corpus Profiler already produced that table, so this turns a full ~1.5h re-NER into a groupby + the
    same (fast, lexicon-based) NRC scoring. Per (document, sentence, PERSON character) a row with the 8 NRC
    emotion scores; character names are normalized across the WHOLE corpus, exactly as analyze_file does
    it. Returns [] if the table lacks the needed columns (the caller then parses)."""
    import pandas as pd
    df = pd.read_csv(conll_path, encoding='utf-8', on_bad_lines='skip')
    formcol = 'Form' if 'Form' in df.columns else ('Word' if 'Word' in df.columns else None)
    if not formcol or not {'NER', 'Sentence ID', 'Document ID'}.issubset(df.columns):
        return []
    has_mwe = 'Multi-Word Expression' in df.columns
    has_doc = 'Document' in df.columns
    rows = []
    canonical_map = {}   # ONE map for the corpus, like analyze_file
    for doc_id, doc_g in df.groupby('Document ID', sort=True):
        doc_link = doc_g['Document'].iloc[0] if has_doc else ''
        for sent_id, g in doc_g.groupby('Sentence ID', sort=True):
            forms = [str(x) for x in g[formcol].tolist() if str(x) != 'nan']
            sent_text = ' '.join(forms)
            # PERSON entities: the Multi-Word Expression column holds the full name (e.g. 'Harry Potter'
            # for both its tokens); fall back to the token Form. Same set semantics as
            # _extract_persons_from_sentence(sent) over sent.ents of type PERSON.
            persons = set()
            for _, r in g[g['NER'].astype(str).str.contains('PERSON', na=False)].iterrows():
                mwe = str(r['Multi-Word Expression']) if has_mwe else ''
                name = (mwe if mwe and mwe.lower() != 'nan' else str(r[formcol])).strip()
                if name and name.lower() != 'nan':
                    persons.add(name)
            scores = _score_sentence_nrc(sent_text)
            normalized = {_normalize_character_name(p, canonical_map) for p in persons} or {"_NARRATOR/UNATTRIBUTED_"}
            for character in normalized:
                row = {
                    'Document ID': int(doc_id) if str(doc_id).isdigit() else doc_id,
                    'Document': doc_link,
                    'Sentence ID': int(sent_id) if str(sent_id).isdigit() else sent_id,
                    'Sentence': sent_text,
                    'Character': character,
                }
                for e in EIGHT_EMOTIONS:
                    row[e.capitalize()] = round(scores[e], 4)
                rows.append(row)
    return rows


def add_corpus_position(df):
    """A single sentence axis for the whole corpus, in document order.

    Sentence IDs restart at 1 in every document, so ordering by Sentence ID
    alone interleaves them - in the Harry Potter corpus, 199 files shuffled
    together, which is not a narrative order at all. Each document is offset by
    the length of the ones before it, giving a position that runs from the first
    sentence of the first document to the last of the last.
    """
    df = df.copy()
    lengths = df.groupby('Document ID')['Sentence ID'].max().sort_index()
    offsets = lengths.cumsum().shift(1).fillna(0).astype(int)
    df['Corpus Position'] = df['Document ID'].map(offsets) + df['Sentence ID']
    return df.sort_values(['Corpus Position', 'Character']).reset_index(drop=True)


# How many of a character's sentences a bin must hold before its average is
# drawn. Below this the average is one or two sentences and swings between 0
# and 1 while everybody else sits at 0.05.
_MIN_SENTENCES_PER_BIN = 3


def _smoothing_window(n, window_size):
    """A window that still smooths something on a long series.

    A 5-sentence window over 14,522 points drawn 12 inches wide is about 1,200
    points to the inch: solid ink, and every apparent spike is one sentence. The
    window grows with the series so that a chart shows roughly 200 turns of the
    line however long the text is.
    """
    return max(window_size, int(n / 200)) if n else window_size


def _smooth(values, window):
    if window > 1 and len(values) >= window:
        return pd.Series(values).rolling(window=window, center=True, min_periods=1).mean().values
    return values


def plot_character_arcs(df, character, outputDir, base_name, window_size=5):
    char_df = df[df['Character'] == character].copy()
    sort_col = 'Corpus Position' if 'Corpus Position' in char_df.columns else 'Sentence ID'
    char_df = char_df.sort_values(sort_col).reset_index(drop=True)

    if len(char_df) < 2:
        return []

    files = []
    fig, ax = plt.subplots(figsize=(12, 6))

    window = _smoothing_window(len(char_df), window_size)
    for emotion in EIGHT_EMOTIONS:
        col = emotion.capitalize()
        smoothed = _smooth(char_df[col].values, window)
        ax.plot(range(len(smoothed)), smoothed, label=emotion.capitalize(),
                color=NRC_COLORS[emotion], linewidth=1.8, alpha=0.85)

    # NOT the sentence number in the text: this character's own appearances, in
    # order. A character absent for fifty pages leaves no gap on their own chart.
    ax.set_xlabel(f'{character}\'s appearances, in order '
                  f'(smoothed over {window} sentences)', fontsize=11)
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


def plot_character_comparison(df, characters, emotion, outputDir, base_name, window_size=5,
                              by_corpus_position=True):
    """One emotion, several characters, on ONE chart.

    Two readings, and both are written out:

      by_corpus_position=True   x is the sentence's place in the CORPUS, so the
                                characters line up: where two arcs cross, they
                                cross at the same moment in the text, and a
                                character who is absent leaves a gap.
      by_corpus_position=False  x is each character's own appearances in order,
                                which compares the SHAPE of their arcs when they
                                appear a very different number of times.

    The first is what the old chart claimed to be and was not: everyone was
    drawn from x=0 against their own count, so Harry ran to 14,522 and Ron
    stopped at 5,177, and it looked as though Harry took over the story.
    """
    have_position = by_corpus_position and 'Corpus Position' in df.columns
    fig, ax = plt.subplots(figsize=(14, 5))
    col = emotion.capitalize()
    colors = plt.cm.tab10.colors

    if have_position:
        # On a shared axis the unit that means anything is a STRETCH of text,
        # not a sentence: five characters' sentence-by-sentence lines over
        # 70,000 positions is ink, not a reading. The corpus is cut into equal
        # bins and each character's average in each bin is plotted, so the
        # lines are comparable at every x - and a bin a character is absent
        # from is a gap in their line rather than a jump across it.
        n_bins = 150
        lo, hi = df['Corpus Position'].min(), df['Corpus Position'].max()
        edges = np.linspace(lo, hi, n_bins + 1)
        centres = (edges[:-1] + edges[1:]) / 2

    for i, character in enumerate(characters):
        char_df = df[df['Character'] == character].sort_values(
            'Corpus Position' if have_position else 'Sentence ID')
        if len(char_df) < 2:
            continue
        if have_position:
            grouped = char_df.groupby(
                pd.cut(char_df['Corpus Position'], bins=edges, include_lowest=True),
                observed=False)[col]
            means, counts = grouped.mean(), grouped.count()
            # A bin holding one sentence is not a reading of that stretch of the
            # text: one sentence that happens to be all anger draws a spike to
            # 1.0 next to everybody else's 0.05. Too little to say -> say
            # nothing, and the line breaks there.
            y = means.where(counts >= _MIN_SENTENCES_PER_BIN).values
            x = centres
        else:
            window = _smoothing_window(len(char_df), window_size)
            y = _smooth(char_df[col].values, window)
            x = range(len(y))
        # thin and semi-transparent: five opaque lines simply painted over one
        # another, whichever was drawn last winning
        ax.plot(x, y, label=f'{character} ({len(char_df)})',
                color=colors[i % len(colors)], linewidth=1.5, alpha=0.8)

    if have_position:
        ax.set_xlabel(f'Sentence position in the corpus, documents in order '
                      f'(averaged over {int((hi - lo) / n_bins)} sentences)', fontsize=11)
    else:
        ax.set_xlabel('Each character\'s own appearances, in order', fontsize=11)
    ax.set_ylabel(f'{col} Intensity', fontsize=11)
    ax.set_title(f'{col} Arc — Character Comparison\n({base_name})', fontsize=13)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    safe_emo = emotion.replace(' ', '_')
    suffix = '' if have_position else '_by_own_appearances'
    out_file = os.path.join(outputDir, f'character_comparison_{safe_emo}{suffix}.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close()
    return out_file


def plot_dominant_emotion_timeline(df, character, outputDir, base_name):
    sort_col = 'Corpus Position' if 'Corpus Position' in df.columns else 'Sentence ID'
    char_df = df[df['Character'] == character].sort_values(sort_col).reset_index(drop=True)
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
    ax.set_xlabel(f'{character}\'s appearances, in order', fontsize=10)
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
         window_size=5, conll_ner_table=None):

    filesToOpen = []

    outputDir = IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                        label='character_emotion_arcs', silent=True)
    if outputDir == '':
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running Character Emotion Arcs at', True)

    outputFilename = IO_files_util.generate_output_file_name(inputFilename, inputDir, outputDir,
                                                              '.csv', 'character_emotion_arcs',
                                                              '', '', '', '', False, True)

    fieldnames = ['Document ID', 'Document', 'Sentence ID', 'Sentence', 'Character'] + \
                 [e.capitalize() for e in EIGHT_EMOTIONS]

    all_rows = []
    # REUSE: when the caller (Corpus Profiler) hands us a Stanza NER CoNLL table it already produced, DERIVE
    # characters + sentences from it -- no re-parse. This pass otherwise builds its OWN Stanza NER pipeline
    # and re-parses the whole corpus (~1.5h on Harry Potter). Falls back to parsing when no table is given.
    if conll_ner_table:
        print('>>> Character Emotion Arcs: derived from an existing Stanza NER table (%s) -- no re-parse'
              % os.path.basename(conll_ner_table))
        try:
            all_rows = analyze_conll_table(conll_ner_table)
        except Exception as e:
            print('Character Emotion Arcs: could not derive from the NER table (%s); parsing instead' % e)
            all_rows = []

    if not all_rows:
        import stanza
        try:
            nlp = stanza.Pipeline(lang='en', processors='tokenize,ner', use_gpu=False)
        except Exception as e:
            mb.showerror(title='Stanza Error',
                         message=f'Could not initialize Stanza NER pipeline.\n\n{str(e)}')
            return filesToOpen
        # ONE canonical name map for the whole corpus: a map per document made
        # Harry, Harry's and Harry Potter three different characters
        canonical_map = {}
        if inputFilename and os.path.exists(inputFilename):
            print("Processing file 1/1 " + os.path.basename(inputFilename))
            all_rows = analyze_file(inputFilename, nlp, 1, canonical_map)
        elif inputDir and os.path.isdir(inputDir):
            txt_files = sorted([f for f in os.listdir(inputDir) if f.endswith('.txt')])
            for doc_id, file in enumerate(txt_files, 1):
                print("Processing file " + str(doc_id) + "/" + str(len(txt_files)) + ' ' + file)
                all_rows.extend(analyze_file(os.path.join(inputDir, file), nlp, doc_id,
                                             canonical_map))

    if not all_rows:
        mb.showwarning(title='No data', message='No text data found to analyze.')
        return filesToOpen

    with open(outputFilename, 'w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    filesToOpen.append(outputFilename)

    df = pd.read_csv(outputFilename)
    # one sentence axis for the corpus, so the charts can put the characters on
    # the same x and a gap means the character is absent
    df = add_corpus_position(df)

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
            # both readings: on the corpus's own sentence axis, where the
            # characters line up and absence shows as a gap, and against each
            # character's own appearances, which compares the SHAPE of arcs
            # belonging to characters who appear very different amounts
            filesToOpen.append(plot_character_comparison(
                df, top_characters, emotion, outputDir, base_name, window_size,
                by_corpus_position=True))
            filesToOpen.append(plot_character_comparison(
                df, top_characters, emotion, outputDir, base_name, window_size,
                by_corpus_position=False))

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
