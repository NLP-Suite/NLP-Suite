# Neural coreference resolution engines for the Coreference GUI (coreference_main.py).
#   - fastcoref (LingMess / F-coref, a BERT/SpanBERT-based neural model) -> the 'BERT' option
#   - coreferee (a coreference component for the spaCy v3 pipeline)       -> the 'spaCy' option
#
# Both mirror the contract of Stanza_util.Stanza_coref: they return (corefed_files, errorFound)
# and, for each input txt file, write
#   1. a coreferenced txt file (pronouns replaced by their referent), and
#   2. a coref_table csv of antecedent (pronoun) -> referent pairs.
# Unlike CoreNLP/Stanza (pronominal only), these models also cluster NOMINAL mentions; to keep the
# downstream coref_table/Sankey format we only REPLACE pronoun mentions, using the first non-pronoun
# mention of a chain as the referent (same rule as the Stanza path).
#
# written for the NLP Suite

import os
import sys
import subprocess
import pandas as pd
import tkinter.messagebox as mb

import GUI_util
import IO_files_util
import IO_user_interface_util

# same pronoun inventory used by the Stanza coref path (Stanza_util._PRONOUNS)
_PRONOUNS = {
    # nominative
    'i', 'you', 'he', 'she', 'it', 'we', 'they',
    # possessive
    'my', 'mine', 'our', 'ours', 'his', 'her', 'hers', 'their', 'theirs', 'its', 'yours',
    # objective
    'me', 'him', 'them',
    # reflexive
    'myself', 'yourself', 'himself', 'herself', 'oneself', 'itself',
    'ourselves', 'yourselves', 'themselves',
}

_COREF_TABLE_COLUMNS = ['Pronoun (antecedent)', 'Referent', 'Sentence ID', 'Sentence',
                        'Document ID', 'Document']


def _is_pronoun(text):
    return text is not None and text.strip().lower() in _PRONOUNS


def _sentence_spans(text):
    """Return a list of (start_char, end_char) sentence spans for `text`, using nltk Punkt.
    Falls back to a single span covering the whole text if nltk/punkt is unavailable."""
    try:
        import nltk
        try:
            tok = nltk.data.load('tokenizers/punkt/english.pickle')
        except LookupError:
            for res in ('punkt', 'punkt_tab'):
                try:
                    nltk.download(res, quiet=True)
                except Exception:
                    pass
            tok = nltk.data.load('tokenizers/punkt/english.pickle')
        return list(tok.span_tokenize(text))
    except Exception:
        return [(0, len(text))]


def _locate_sentence(char_pos, sent_spans, text):
    """Map a character offset to a 1-based sentence index and the sentence text."""
    for idx, (s, e) in enumerate(sent_spans, 1):
        if s <= char_pos < e:
            return idx, text[s:e].strip()
    # position past the last boundary: attribute to the last sentence
    if sent_spans:
        s, e = sent_spans[-1]
        return len(sent_spans), text[s:e].strip()
    return 1, text.strip()


def _make_output_dir(inputFilename, inputDir, outputDir, engine):
    if inputFilename != '':
        inputBaseName = os.path.basename(inputFilename)[0:-4]
    else:
        inputBaseName = os.path.basename(inputDir)
    outputCorefDir = os.path.join(outputDir, 'coref_' + engine + '_' + inputBaseName)
    return IO_files_util.make_output_subdirectory('', '', outputCorefDir, '', silent=False)


def _apply_char_replacements(text, replacements):
    """Rebuild `text` applying a list of (start_char, end_char, replacement_string), non-overlapping."""
    if not replacements:
        return text
    replacements = sorted(replacements, key=lambda r: r[0])
    out = []
    cursor = 0
    for start, end, rep in replacements:
        if start < cursor:  # overlapping span; skip to stay safe
            continue
        out.append(text[cursor:start])
        out.append(rep)
        cursor = end
    out.append(text[cursor:])
    return ''.join(out)


def _write_outputs(engine, coref_rows, per_file_corefed, outputCorefedDir):
    """Write coreferenced txt files (already computed as (path_tail, corefed_text)) and the coref_table csv.
    Returns the list of output files."""
    corefed_files = []
    for tail, corefed_text in per_file_corefed:
        corefed_filename = os.path.join(outputCorefedDir, tail)
        with open(corefed_filename, 'w', encoding='utf-8') as f:
            f.write(corefed_text)
        corefed_files.append(corefed_filename)
    if len(coref_rows) > 0:
        coref_table_filename = os.path.join(outputCorefedDir, 'coref_table_' + engine + '.csv')
        pd.DataFrame(coref_rows, columns=_COREF_TABLE_COLUMNS).to_csv(
            coref_table_filename, index=False, encoding='utf-8')
        corefed_files.append(coref_table_filename)
    return corefed_files


# ======================================================================================
#  BERT option  ->  fastcoref (LingMess / F-coref)
# ======================================================================================
def fastcoref_coref(config_filename, inputFilename, inputDir, outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
                    language_var, manual_Coref):
    """Coreference resolution with fastcoref (a BERT/SpanBERT-based neural model).
    Returns (corefed_files, errorFound) to match coreference_main.run()."""
    if language_var != 'English':
        mb.showwarning(title='Language',
                       message='The BERT (fastcoref) coreference model wired here is English only.\n\n'
                               'The selected language is ' + str(language_var) + '.')
        return [], True

    try:
        from fastcoref import FCoref
    except ImportError:
        mb.showerror(title='fastcoref not installed',
                     message="The BERT coreference option requires the 'fastcoref' package, which is not installed.\n\n"
                             "To install it, open a terminal and run:\n"
                             "   conda activate NLP\n"
                             "   pip install fastcoref\n\n"
                             "fastcoref uses PyTorch + Transformers (already bundled with the NLP Suite) and, "
                             "on first use, downloads its model (~500 MB) - so the first run needs an internet connection.")
        return [], True

    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt',
                                          silent=False, configFileName=config_filename)
    if len(inputDocs) == 0:
        return [], True

    outputCorefedDir = _make_output_dir(inputFilename, inputDir, outputDir, 'BERT')
    if outputCorefedDir == '':
        return [], True

    startTime = IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis start',
        'Started running BERT (fastcoref) coreference resolution at', True, '', True, '', False)

    try:
        model = FCoref()  # first call downloads the model
    except Exception as e:
        mb.showerror(title='fastcoref model error',
                     message='Failed to load the fastcoref model.\n\n' + str(e) +
                             '\n\nThe first run downloads the model and needs an internet connection.')
        return [], True

    coref_rows = []
    per_file_corefed = []
    errorFound = False
    nDocs = len(inputDocs)

    for docID, doc_path in enumerate(inputDocs, 1):
        tail = os.path.basename(doc_path)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        text = open(doc_path, 'r', encoding='utf-8', errors='ignore').read()
        if text.strip() == '':
            print("  Skipping empty file: " + tail)
            continue

        try:
            preds = model.predict(texts=[text])
            clusters = preds[0].get_clusters(as_strings=False)  # list of clusters of (start,end) char spans
        except Exception as e:
            print("  Error processing " + tail + ": " + str(e))
            errorFound = True
            per_file_corefed.append((tail, text))  # keep the original so no document is silently dropped
            continue

        sent_spans = _sentence_spans(text)
        replacements = []  # (start, end, replacement)

        for cluster in clusters:
            # canonical referent = first non-pronoun mention in the cluster
            canonical = None
            for (s, e) in cluster:
                mention_text = text[s:e].strip()
                if mention_text and not _is_pronoun(mention_text):
                    canonical = mention_text
                    break
            if canonical is None:
                continue
            for (s, e) in cluster:
                mention_text = text[s:e]
                if _is_pronoun(mention_text):
                    sent_idx, sent_text = _locate_sentence(s, sent_spans, text)
                    coref_rows.append([mention_text.strip(), canonical, sent_idx, sent_text,
                                       docID, doc_path])
                    replacements.append((s, e, canonical))

        corefed_text = _apply_char_replacements(text, replacements)
        per_file_corefed.append((tail, corefed_text))

    corefed_files = _write_outputs('BERT', coref_rows, per_file_corefed, outputCorefedDir)

    IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis end',
        'Finished running BERT (fastcoref) coreference resolution at', True, '', True, startTime, False)

    _maybe_manual(manual_Coref, inputDir, inputFilename, corefed_files)
    return corefed_files, errorFound


# ======================================================================================
#  spaCy option  ->  coreferee
# ======================================================================================
def coreferee_coref(config_filename, inputFilename, inputDir, outputDir,
                    openOutputFiles, chartPackage, dataTransformation,
                    language_var, manual_Coref):
    """Coreference resolution with coreferee running in the spaCy v3 pipeline.
    Returns (corefed_files, errorFound) to match coreference_main.run()."""
    if language_var != 'English':
        mb.showwarning(title='Language',
                       message='The spaCy (coreferee) coreference model wired here is English only.\n\n'
                               'The selected language is ' + str(language_var) + '.')
        return [], True

    try:
        import spacy
        import coreferee  # noqa: F401  (registers the 'coreferee' pipeline factory)
    except ImportError:
        mb.showerror(title='coreferee not installed',
                     message="The spaCy coreference option requires the 'coreferee' package, which is not installed.\n\n"
                             "To install it, open a terminal and run:\n"
                             "   conda activate NLP\n"
                             "   pip install coreferee\n\n"
                             "The spaCy and coreferee English models are downloaded automatically on first use.")
        return [], True

    # Load a spaCy English model, preferring larger models coreferee is trained against; if none is
    # installed, download the small one on first use (same one-time-download pattern as spaCy_util).
    nlp = None
    for model_name in ('en_core_web_lg', 'en_core_web_md', 'en_core_web_trf', 'en_core_web_sm'):
        try:
            nlp = spacy.load(model_name)
            break
        except Exception:
            continue
    if nlp is None:
        try:
            IO_user_interface_util.timed_alert(
                GUI_util.window, 6000, 'spaCy model download',
                'Downloading the spaCy English model "en_core_web_sm" for the first time.\n\n'
                'This is a one-time download. Please be patient.', False)
            subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
            nlp = spacy.load('en_core_web_sm')
        except Exception as e:
            mb.showerror(title='spaCy model download failed',
                         message="Could not download a spaCy English model for coreferee.\n\n" + str(e) +
                                 "\n\nCheck your internet connection, or install one manually:\n"
                                 "   python -m spacy download en_core_web_sm")
            return [], True

    # Add coreferee to the pipeline; if its English model is missing, install it once and retry
    # (coreferee ships its coref model separately from pip, via 'python -m coreferee install en').
    try:
        nlp.add_pipe('coreferee')
    except Exception:
        try:
            IO_user_interface_util.timed_alert(
                GUI_util.window, 6000, 'coreferee model download',
                'Installing the coreferee English model for the first time.\n\n'
                'This is a one-time download. Please be patient.', False)
            subprocess.check_call([sys.executable, '-m', 'coreferee', 'install', 'en'])
            nlp.add_pipe('coreferee')
        except Exception as e:
            mb.showerror(title='coreferee model install failed',
                         message="Could not install the coreferee English model.\n\n" + str(e) +
                                 "\n\nCheck your internet connection, or install it manually:\n"
                                 "   python -m coreferee install en")
            return [], True

    inputDocs = IO_files_util.getFileList(inputFilename, inputDir, fileType='.txt',
                                          silent=False, configFileName=config_filename)
    if len(inputDocs) == 0:
        return [], True

    outputCorefedDir = _make_output_dir(inputFilename, inputDir, outputDir, 'spaCy')
    if outputCorefedDir == '':
        return [], True

    startTime = IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis start',
        'Started running spaCy (coreferee) coreference resolution at', True, '', True, '', False)

    coref_rows = []
    per_file_corefed = []
    errorFound = False
    nDocs = len(inputDocs)

    for docID, doc_path in enumerate(inputDocs, 1):
        tail = os.path.basename(doc_path)
        print("Processing file " + str(docID) + "/" + str(nDocs) + ' ' + tail)
        text = open(doc_path, 'r', encoding='utf-8', errors='ignore').read()
        if text.strip() == '':
            print("  Skipping empty file: " + tail)
            continue

        try:
            doc = nlp(text)
        except Exception as e:
            print("  Error processing " + tail + ": " + str(e))
            errorFound = True
            per_file_corefed.append((tail, text))
            continue

        # token index -> replacement string ('' marks a non-leading token of a replaced pronoun)
        replacements = {}
        sent_index_of_token = {}
        for si, sent in enumerate(doc.sents, 1):
            for tok in sent:
                sent_index_of_token[tok.i] = (si, sent.text.strip())

        chains = getattr(doc._, 'coref_chains', None) or []
        for chain in chains:
            # the most specific mention in the chain is coreferee's canonical referent
            try:
                canonical_mention = chain[chain.most_specific_mention_index]
                canonical = ' '.join(doc[i].text for i in canonical_mention.token_indexes)
            except Exception:
                continue
            if not canonical or _is_pronoun(canonical):
                continue
            for mention in chain:
                idxs = list(mention.token_indexes)
                mention_text = ' '.join(doc[i].text for i in idxs)
                if _is_pronoun(mention_text):
                    first = idxs[0]
                    si, sent_text = sent_index_of_token.get(first, (1, ''))
                    coref_rows.append([mention_text.strip(), canonical, si, sent_text,
                                       docID, doc_path])
                    for pos, ti in enumerate(idxs):
                        replacements[ti] = canonical if pos == 0 else ''

        # rebuild text token-by-token, preserving original whitespace
        out = []
        for tok in doc:
            if tok.i in replacements:
                rep = replacements[tok.i]
                if rep:
                    out.append(rep + tok.whitespace_)
                # else: trailing token of a multi-word pronoun mention -> drop
            else:
                out.append(tok.text_with_ws)
        per_file_corefed.append((tail, ''.join(out)))

    corefed_files = _write_outputs('spaCy', coref_rows, per_file_corefed, outputCorefedDir)

    IO_user_interface_util.timed_alert(
        GUI_util.window, 2000, 'Analysis end',
        'Finished running spaCy (coreferee) coreference resolution at', True, '', True, startTime, False)

    _maybe_manual(manual_Coref, inputDir, inputFilename, corefed_files)
    return corefed_files, errorFound


def _maybe_manual(manual_Coref, inputDir, inputFilename, corefed_files):
    """Reuse the CoreNLP split-screen manual editor (single-file input only), as the Stanza path does."""
    if not manual_Coref:
        return
    if len(inputDir) == 0 and len(inputFilename) > 0:
        import Stanford_CoreNLP_coreference_util
        for file in corefed_files:
            if file.endswith('.txt'):
                Stanford_CoreNLP_coreference_util.manualCoref(inputFilename, file, file)
    else:
        IO_user_interface_util.timed_alert(
            GUI_util.window, 2000, 'Feature Not Available',
            'Manual coreference is only available when processing a single file, not an input directory.')
