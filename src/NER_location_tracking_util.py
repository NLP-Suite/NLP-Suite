import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "NER_location_tracking_util",
        ['os', 'tkinter', 'pandas', 'stanza']) == False:
    sys.exit(0)

import os
import pandas as pd
import tkinter.messagebox as mb
from collections import defaultdict

import IO_csv_util
import IO_files_util
import IO_user_interface_util


PERSON_TAGS = {'PERSON'}
LOCATION_TAGS = {'GPE', 'LOC', 'STATE_OR_PROVINCE', 'COUNTRY', 'CITY', 'LOCATION', 'FAC'}


def _get_stanza_pipeline(language='en'):
    import stanza
    try:
        nlp = stanza.Pipeline(lang=language, processors='tokenize,ner', use_gpu=False, verbose=False)
    except Exception:
        stanza.download(language, verbose=False)
        nlp = stanza.Pipeline(lang=language, processors='tokenize,ner', use_gpu=False, verbose=False)
    return nlp


def _extract_cooccurrences(filepath, nlp, doc_id):
    """Extract person-location co-occurrences per sentence from a text file."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if not text.strip():
        return []

    doc = nlp(text)
    rows = []
    for sent_idx, sentence in enumerate(doc.sentences):
        persons = []
        locations = []
        for ent in sentence.entities:
            if ent.type in PERSON_TAGS:
                if ent.text not in persons:
                    persons.append(ent.text)
            elif ent.type in LOCATION_TAGS:
                if ent.text not in locations:
                    locations.append(ent.text)

        if persons and locations:
            sent_text = sentence.text
            for person in persons:
                for location in locations:
                    rows.append({
                        'Entity': person,
                        'Location': location,
                        'Sentence ID': sent_idx + 1,
                        'Sentence': sent_text,
                        'Document ID': doc_id,
                        'Document': os.path.basename(filepath)
                    })

    return rows


def main(inputFilename, inputDir, outputDir, chartPackage='', dataTransformation='',
         language='en'):
    """Extract entity-location co-occurrences from text files using Stanza NER.

    For each sentence that mentions both a PERSON and a LOCATION, creates a row
    pairing them. The output CSV is ready for the animated movement map.

    Parameters
    ----------
    inputFilename : str   Single input text file (or '' if using inputDir).
    inputDir : str        Directory of text files (or '' if using inputFilename).
    outputDir : str       Output directory.
    chartPackage : str    Not used currently, reserved for future chart generation.
    dataTransformation : str  Not used currently.
    language : str        Stanza language code (default 'en').

    Returns
    -------
    list of str   Paths to output files.
    """
    filesToOpen = []

    if inputFilename == '' and inputDir == '':
        mb.showwarning("Warning",
                       "No input file or directory specified.\n\nPlease select a txt file or directory and try again.")
        return filesToOpen

    files = []
    if inputDir:
        for f in sorted(os.listdir(inputDir)):
            if f.endswith('.txt'):
                files.append(os.path.join(inputDir, f))
    elif inputFilename:
        files = [inputFilename]

    if not files:
        mb.showwarning("Warning", "No .txt files found in the input.")
        return filesToOpen

    startTime = IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis start',
                                                    'Started running entity-location tracking.\n\nStanza NER model loading...',
                                                    True, '', True, '', False)

    nlp = _get_stanza_pipeline(language)

    all_rows = []
    for doc_id, filepath in enumerate(files, 1):
        print(f"  Processing ({doc_id}/{len(files)}): {os.path.basename(filepath)}")
        rows = _extract_cooccurrences(filepath, nlp, doc_id)
        all_rows.extend(rows)

    if not all_rows:
        mb.showwarning("No results",
                       "No sentences found containing both a person and a location.\n\n"
                       "This can happen if your texts don't mention named people and places in the same sentences.")
        return filesToOpen

    df = pd.DataFrame(all_rows)

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename if inputFilename else inputDir, inputDir, outputDir,
        '.csv', 'NER_entity_location_tracking')
    df.to_csv(outputFilename, index=False, encoding='utf-8')
    filesToOpen.append(outputFilename)
    print(f"  Entity-location tracking: {len(df)} co-occurrences from {len(files)} document(s)")

    summary = df.groupby(['Entity', 'Location']).agg(
        Count=('Sentence ID', 'size'),
        First_Sentence=('Sentence ID', 'min'),
        Documents=('Document', lambda x: ', '.join(sorted(x.unique())))
    ).reset_index().sort_values(['Entity', 'First_Sentence'])

    summaryFilename = IO_files_util.generate_output_file_name(
        inputFilename if inputFilename else inputDir, inputDir, outputDir,
        '.csv', 'NER_entity_location_summary')
    summary.to_csv(summaryFilename, index=False, encoding='utf-8')
    filesToOpen.append(summaryFilename)

    IO_user_interface_util.timed_alert(GUI_util.window, 2000, 'Analysis end',
                                       'Finished running entity-location tracking at', True, '', True, startTime)

    return filesToOpen
