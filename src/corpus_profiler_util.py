# corpus_profiler_util.py
#
# Orchestration + report generation for the Corpus Profiler (corpus_profiler_main.py).
#
# The profiler runs a battery of analyses with sensible DEFAULTS and produces a single
# navigable HTML report, NLP_corpus_profile.html -- the only file auto-opened. The many
# individual output files (csv/xlsx/png/html/kml) are linked FROM the report ("depth on demand").
#
# Design (see docs/corpus_profiler_spec.md):
#   * Each analysis is a REGISTRY entry tagged with a category, a kind ('batch' | 'gui'),
#     a human label, and a runner that invokes the underlying *_util function with defaults.
#   * BATCH analyses call the util function directly and return their output-file list.
#   * openOutputFiles is forced False for every underlying tool -- ONLY the report opens.
#   * Moving an analysis between categories is a one-line change (the category field).
#
# Phase 0 wires categories: counts, vocabulary, entities. The runners are grounded in the exact
# working calls of the underlying analysis GUIs. Heavy imports are done lazily inside the
# runners so the report generator (build_report) stays importable/testable on its own.

import os
import html as _html

# ---------------------------------------------------------------------------------------------
# Category metadata (order + user-question titles). Adding/moving categories is done here.
# ---------------------------------------------------------------------------------------------
CATEGORY_ORDER = ['counts', 'syntax', 'semantics',
                  'topics', 'entities', 'spatial', 'narrative', 'sentiment', 'characters']

CATEGORY_TITLE = {
    'counts':    'How big / how varied?  (Counts, measures, vocabulary & entities)',
    'syntax':    'Grammar & structure — parts of speech  (Syntax)',
    'semantics': 'What do the words mean?  (Semantics)',
    'topics':    'What is it about?  (Topics)',
    'entities':  'Who said what, and when?  (gender, dialogue, dates — CoreNLP)',
    'spatial':   'Where does it all happen?  (geocodable and symbolic space)',
    'narrative': 'Who did what to whom?  (Narrative)',
    'sentiment': 'How does it feel?  (Sentiment)',
    'characters': "Zooming in on characters: Characters' emotional arcs and movements in time and space",
}


# ---------------------------------------------------------------------------------------------
# Batch runners. Each takes the shared context dict `c` and returns a list of output file paths.
# They lazily import the underlying util module so this file imports cleanly for report testing.
# Signatures are taken verbatim from the working calls in each analysis GUI's run().
# ---------------------------------------------------------------------------------------------
def _analysis_dir(c, label, sub=''):
    """A subfolder of the profile for ONE analysis's files. The profile folder if it cannot be made.

    *sub* nests a plain child inside it, WITHOUT repeating the corpus name: two kinds of space belong
    together under GIS_<corpus>/geocodable and GIS_<corpus>/symbolic, and naming the corpus at every
    level is what put paths over Windows' 260-character limit twice in one day.

    The report promises that "every individual output file is written to a category subfolder and
    LINKED from the report", and most analyses honour it because the utils they call make their own
    subfolder. Seven did not, and wrote straight into the profile folder: 40 loose files - fifteen
    from the semantic classes alone, and a 2.1 GB vector dump - in the one folder a reader opens.

    NOT IO_files_util.make_output_subdirectory: that DELETES an existing folder (shutil.rmtree, and
    with silent=True it does it without asking). Reuse depends on those files still being there, so
    the folder is created only when absent and otherwise used as it stands. The naming follows the
    same rule, so folders sit alongside the ones the utils make.
    """
    outputDir = c.get('outputDir') or ''
    if not outputDir or not label:
        return outputDir
    if c.get('inputFilename'):
        stem = os.path.basename(str(c['inputFilename']))
        stem = stem[:-4] if stem.lower().endswith('.txt') else os.path.splitext(stem)[0]
    elif c.get('inputDir'):
        stem = os.path.basename(os.path.normpath(str(c['inputDir'])))
    else:
        stem = ''
    path = os.path.join(outputDir, (label + '_' + stem) if stem else label)
    if sub:
        path = os.path.join(path, sub)
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print('Corpus Profiler: could not make the %s subfolder (%s); writing beside the report'
              % (label, e))
        return outputDir
    return path


def _files(result):
    """Normalize a util return (str | list | (list, x) | None) into a flat list of paths."""
    if result is None:
        return []
    if isinstance(result, tuple):
        result = result[0]
    if isinstance(result, str):
        return [result]
    if isinstance(result, (list, set)):
        return [f for f in result if isinstance(f, str) and f]
    return []


# ---- counts -------------------------------------------------------------------------------
def _run_statistics(c):
    import statistics_txt_util
    out, _ = statistics_txt_util.compute_corpus_statistics(
        c['window'], c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename'], False,
        c['chartPackage'], c['dataTransformation'])
    return _files(out)

def _run_ngrams(c):
    import statistics_txt_util
    # signature: (window, inputFilename, inputDir, outputDir, configFileName,
    #             ngramsNumber, frequency, hapax_words, normalize, lemmatize=False, ...)
    # ngramsNumber/frequency/hapax_words/normalize are REQUIRED. Defaults mirror the N-grams GUI:
    # size 3, min frequency 1, compute hapax, no normalization. Pass the trailing options by
    # KEYWORD so we never have to fill (and risk misaligning) every optional positional in between.
    out, _ = statistics_txt_util.compute_character_word_ngrams(
        c['window'], c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename'],
        3, 1, True, False,
        wordgram=True, openOutputFiles=False,
        chartPackage=c['chartPackage'], dataTransformation=c['dataTransformation'])
    return _files(out)

def _sentence_length_from_conll(conll_path, c):
    """Build the sentence-length table + chart by GROUPING an existing CoNLL parse (one token row each,
    with Sentence ID + Document ID) -- no parsing. Same output columns/filename/chart as the stock
    compute_sentence_length, so the summary reads it identically. [] if the table lacks the needed columns
    or anything goes wrong (the caller then falls back to a real parse)."""
    try:
        import pandas as pd
        import IO_files_util
        import charts_util
        df = pd.read_csv(conll_path, encoding='utf-8', on_bad_lines='skip')
        if not {'Form', 'Sentence ID', 'Document ID'}.issubset(df.columns):
            return []
        outdir = IO_files_util.make_output_subdirectory(c['inputFilename'], c['inputDir'], c['outputDir'],
                                                        label='Statistics_txt_sent_length', silent=True)
        if not outdir:
            return []
        outfile = IO_files_util.generate_output_file_name(c['inputFilename'], c['inputDir'], outdir, '.csv',
                                                          'sentence_length')
        has_doc = 'Document' in df.columns
        rows = []
        # token COUNT per (document, sentence) is the sentence length; join Forms for the sentence text
        for (docid, sentid), g in df.groupby(['Document ID', 'Sentence ID'], sort=True):
            forms = [str(x) for x in g['Form'].tolist() if str(x) != 'nan']
            rows.append([len(forms), int(sentid) if str(sentid).isdigit() else sentid, ' '.join(forms),
                         int(docid) if str(docid).isdigit() else docid,
                         g['Document'].iloc[0] if has_doc else ''])
        out_df = pd.DataFrame(rows, columns=['Sentence length (in words)', 'Sentence ID', 'Sentence',
                                             'Document ID', 'Document'])
        out_df.to_csv(outfile, index=False, encoding='utf-8')
        files = [outfile]
        charts = charts_util.plot(outfile, outdir, columns=['Sentence length (in words)'],
                                  title='Sentence Length (In Words)', x_label='Sentence length (in words)',
                                  file_label='Sent', plot_list=['Sentence length (in words)'],
                                  title_label='Sentence Lengths')
        if charts:
            files += charts if isinstance(charts, list) else [charts]
        return files
    except Exception as e:
        print('Corpus Profiler: sentence-length-from-parse failed (%s); parsing instead' % e)
        return []


def _run_sentence_length(c):
    # FAST PATH: the corpus is already Stanza-parsed (POS and/or NER), and BOTH CoNLL tables carry Form +
    # Sentence ID + Document ID -- so sentence lengths are a GROUPBY, not a third parse. The stock
    # compute_sentence_length runs a full Stanza pipeline per document AND AGAIN per sentence (~O(#sentences)
    # pipeline calls -> ~1h25m on Harry Potter, longer than the neural NER parse). Derive from the cached
    # parse when we have one; fall back to the stock function otherwise.
    conll = (_find_existing_pos_csv(c) or _find_existing_ner_csv(c))
    if conll:
        out = _sentence_length_from_conll(conll[0], c)
        if out:
            print('>>> Sentence length: derived from the existing Stanza parse (%s) -- no re-parse'
                  % os.path.basename(conll[0]))
            return out
    import statistics_txt_util
    return _files(statistics_txt_util.compute_sentence_length(
        c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename'],
        c['chartPackage'], c['dataTransformation']))

def _run_line_length(c):
    import statistics_txt_util
    return _files(statistics_txt_util.compute_line_length(
        c['window'], c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation']))

# NOTE: _run_language_detection() was REMOVED from the profiler (2026-07-16). It ran THREE detectors
# (langdetect, langid, spaCy) over EVERY file -- slow on a large corpus -- to re-confirm the language the
# user already declared in the I/O configuration (the summary header states it). Nothing interpreted its
# output, so it contributed no finding to the report. Language detection remains available on its own from
# the menu: "Language detection" -> style_analysis_main.py.


# ---- vocabulary ---------------------------------------------------------------------------
def _run_yule(c):
    import statistics_txt_util
    return _files(statistics_txt_util.yule(
        c['window'], c['inputFilename'], c['inputDir'], _analysis_dir(c, 'vocabulary_richness'),
        c['config_filename']))

def _run_word_shape(keyword):
    # process_words(window, configFileName, inputFilename, inputDir, outputDir, openOutputFiles,
    #   chartPackage, dataTransformation, processType='', language='English', ...) -- processType is
    #   the menu keyword it switches on ('Hapax legomena', 'capital', 'Vowel', 'Word length', ...)
    def runner(c):
        import statistics_txt_util
        # one folder per shape, named after the keyword: 'capital' alone wrote nine loose files
        label = 'words_' + str(keyword).replace(' ', '_').lower()
        return _files(statistics_txt_util.process_words(
            c['window'], c['config_filename'], c['inputFilename'], c['inputDir'],
            _analysis_dir(c, label),
            False, c['chartPackage'], c['dataTransformation'], keyword, c['language']))
    return runner

def _run_hapax(c):
    return _run_word_shape('Hapax legomena')(c)

def _run_unusual_words(c):
    import file_spell_checker_util
    return _files(file_spell_checker_util.nltk_unusual_words(
        c['window'], c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename'],
        False, c['chartPackage'], c['dataTransformation']))

def _run_abstract_concrete(c):
    import style_analysis_abstract_concreteness_analysis_util as _abs
    return _files(_abs.main(
        c['window'], c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename'],
        False, c['chartPackage'], c['dataTransformation'], processType=''))

def _run_iconic(c):
    import style_analysis_iconicity_analysis_util as _icon
    return _files(_icon.main(
        c['window'], c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename'],
        False, c['chartPackage'], c['dataTransformation'], processType='', use_defaults=True))

def _run_tfidf(c):
    import statistics_corpus_tfidf_util
    return _files(statistics_corpus_tfidf_util.compute_tfidf(
        c['inputFilename'], c['inputDir'], c['outputDir'], c['chartPackage'], c['dataTransformation']))

def _run_lexical_diversity(c):
    import statistics_corpus_lexical_diversity_util
    return _files(statistics_corpus_lexical_diversity_util.compute_lexical_diversity(
        c['inputFilename'], c['inputDir'], c['outputDir'], c['chartPackage'], c['dataTransformation']))

def _run_word_frequency(c):
    import statistics_corpus_word_frequency_util
    return _files(statistics_corpus_word_frequency_util.compute_word_frequency(
        c['inputFilename'], c['inputDir'], c['outputDir'], c['chartPackage'], c['dataTransformation']))


# ---- entities (English + Stanford CoreNLP) ------------------------------------------------
def _configured_parser_tag(c):
    """The filename token for the parser the config-aware runners WOULD use ('corenlp' / 'spacy' /
    'stanza'). Mirrors the identical dispatch in _run_ner and _run_svo, so the reuse probes can never hand
    back a table produced by a DIFFERENT parser than the configured one -- reusing a CoreNLP table under a
    Stanza config would silently undo the point of making those passes config-aware."""
    if _is_corenlp_package(c.get('package')) and _corenlp_available():
        return 'corenlp'
    if 'spacy' in str(c.get('package', '')).lower():
        return 'spacy'
    return 'stanza'


# ---------------------------------------------------------------------------------------------
# Provenance: WHICH CODE wrote a reusable table.
#
# The reuse probes below gate on filename, columns and size -- what a file IS, never what MADE it. So
# a table written by an older, buggier version of an analysis is reused without a murmur, and the run
# prints "no re-parse" while quietly building on stale data. That is the same class of mistake as a
# stale cache anywhere else: cheap when right, invisible when wrong.
#
# Each reusable table therefore gets a small sidecar recording a fingerprint of the SOURCE MODULES that
# produce it. On reuse the fingerprint is recomputed and compared: same code, reuse; different code,
# re-run just that analysis. Not the release number -- a release bump would invalidate everything and
# make a one-line fix cost a full re-parse.
#
# The sidecar records a second thing: WHICH CORPUS the table was built from. The probes search the
# output directory by filename and columns, and nothing in that ties a table to the text it came from --
# the "prior run on THIS corpus" in the probe's docstring is an assumption resting on one output
# directory per corpus. Point the profiler at a second corpus while keeping the old output directory
# (running a coreference-resolved copy alongside the original is the obvious way to do it) and the probe
# finds the FIRST corpus's table, matches name and columns, passes the module check because the code did
# not change, and reuses it. The two runs then agree perfectly, because they are the same numbers.
#
# What it cannot see: a change in a downloaded model or an external lexicon, and a change in a helper
# not named here. Missing or unreadable sidecar means "cannot verify", which reuses and says so, rather
# than forcing every existing profile to re-parse once.
# ---------------------------------------------------------------------------------------------
PROVENANCE_SUFFIX = '.provenance.json'

# The modules whose code decides what goes INTO each kind of reusable table. Every name here was
# checked to exist: a name that does not is skipped silently, which would quietly weaken the check.
_PROVENANCE_MODULES = {
    'ner':       ['Stanza_util', 'Stanford_CoreNLP_util', 'spaCy_util'],
    'pos':       ['Stanza_util', 'Stanford_CoreNLP_util', 'spaCy_util'],
    'svo':       ['SVO_util', 'Stanza_util', 'Stanford_CoreNLP_util', 'spaCy_util'],
    'sentiment': ['Stanza_util', 'sentiment_analysis_VADER_util', 'sentiment_analysis_ANEW_util',
                  'sentiment_analysis_NRC_util', 'sentiment_analysis_SentiWordNet_util',
                  'sentiment_analysis_hedonometer_util'],
    'srl':       ['SRL_util', 'SRL_worker'],
}


def _module_fingerprint(kind):
    """A hash of the source of the modules that produce *kind* of table.

    Only modules that exist are hashed, and their names go into the stamp, so a rename shows up as a
    changed fingerprint rather than as a silent gap.
    """
    import hashlib
    src_dir = os.path.dirname(os.path.abspath(__file__))
    digest = hashlib.sha256()
    seen = []
    for name in sorted(_PROVENANCE_MODULES.get(kind, [])):
        path = os.path.join(src_dir, name + '.py')
        if not os.path.isfile(path):
            continue
        try:
            with open(path, 'rb') as fh:
                digest.update(name.encode('utf-8'))
                digest.update(fh.read())
            seen.append(name)
        except OSError:
            continue
    return (digest.hexdigest()[:16] if seen else ''), seen


# Bookkeeping files that live in a corpus folder without being corpus content. Kept in step with
# IO_files_util.SIDECAR_FILES but spelled out here on purpose: this must hold when IO_files_util is a
# test stub, and a mock's is_sidecar_file() returns a truthy mock, which would skip EVERY document and
# silently fingerprint an empty corpus.
_CORPUS_SIDECARS = {'_pkl_version.txt', '_pkl_version.dat', 'gis_settings.json',
                    'desktop.ini', 'thumbs.db', '.ds_store'}


def corpus_fingerprint(c):
    """(digest, label) identifying the corpus in *c*, or ('', '') when it cannot be determined.

    Names and sizes, never contents: a corpus is thousands of files and this runs before every reuse
    decision, so reading them would cost more than the re-parse it is trying to avoid. Name+size is
    enough for the job -- it separates two different corpora, and it separates a corpus from an edited
    copy of itself, which is exactly when a stale table must not be reused.

    Deliberately NOT part of the digest: the directory path. The same corpus moved or renamed is still
    the same corpus, and invalidating on a path would re-parse for nothing. The path goes in as a
    human-readable *label* instead, so a mismatch message can name the two corpora.
    """
    import hashlib
    inputDir = (c or {}).get('inputDir') or ''
    inputFilename = (c or {}).get('inputFilename') or ''
    entries = []
    if inputDir and os.path.isdir(inputDir):
        label = os.path.basename(os.path.normpath(inputDir))
        for root, _dirs, files in os.walk(inputDir):
            for name in files:
                if name.endswith(PROVENANCE_SUFFIX) or name.lower() in _CORPUS_SIDECARS:
                    continue
                full = os.path.join(root, name)
                try:
                    size = os.path.getsize(full)
                except OSError:
                    continue
                entries.append((os.path.relpath(full, inputDir).replace(os.sep, '/').lower(), size))
    elif inputFilename and os.path.isfile(inputFilename):
        label = os.path.basename(inputFilename)
        try:
            entries.append((label.lower(), os.path.getsize(inputFilename)))
        except OSError:
            return '', ''
    else:
        return '', ''
    if not entries:
        return '', label
    digest = hashlib.sha256()
    for name, size in sorted(entries):
        digest.update(('%s|%d\n' % (name, size)).encode('utf-8'))
    return digest.hexdigest()[:16], label


def stamp_provenance(paths, kind, c=None):
    """Record which code produced these tables.

    Records which CODE produced the table and, when *c* is given, which CORPUS it was built from -- the
    two questions a later run has to answer before reusing it.

    A failure here is SAID, not swallowed: an unwritten stamp means the next run cannot tell whether
    reusing the table is safe, and it would report that as "no provenance stamp" as though the file
    were simply old. The stamp is written whole and then moved into place, so a failure never leaves
    a truncated one behind (which is what an earlier version of this did).
    """
    import json
    import time
    fingerprint, modules = _module_fingerprint(kind)
    if not fingerprint:
        print('Corpus Profiler: no %s modules found to fingerprint; tables left unstamped' % kind)
        return
    corpus_fp, corpus_label = corpus_fingerprint(c) if c is not None else ('', '')
    for p in paths or []:
        target = str(p) + PROVENANCE_SUFFIX
        tmp = target + '.tmp'
        try:
            record = {'kind': kind, 'fingerprint': fingerprint, 'modules': modules,
                      'written': time.strftime('%Y-%m-%d %H:%M:%S')}
            if corpus_fp:
                record['corpus'] = corpus_fp
                record['corpus_label'] = corpus_label
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(record, fh, indent=1)
            os.replace(tmp, target)
        except Exception as e:
            print('Corpus Profiler: could not stamp %s (%s)' % (os.path.basename(str(p)), e))
            try:
                os.remove(tmp)
            except OSError:
                pass


def provenance_is_current(path, kind, c=None):
    """(ok, why) for reusing *path*: same code, and same corpus?

    ok=True with why='' when both match, ok=True with a why when something cannot be checked (an older
    profile, an unreadable stamp), ok=False when the code that wrote it has since changed OR it was
    built from a different corpus.

    The corpus check is deliberately asymmetric. A MISMATCH is refused -- reusing another corpus's
    table is silent, total corruption of the result, and no amount of saved time is worth it. An
    UNVERIFIABLE stamp (one written before corpora were recorded) is reused with a spoken reason,
    because refusing would re-parse every profile built before this change for a risk that is usually
    theoretical. Separate output directories per corpus remain the real guarantee.
    """
    import json
    stamp_path = str(path) + PROVENANCE_SUFFIX
    if not os.path.isfile(stamp_path):
        return True, 'no provenance stamp (written before stamping, or by another tool)'
    try:
        with open(stamp_path, encoding='utf-8') as fh:
            stamped = json.load(fh)
    except Exception:
        return True, 'provenance stamp unreadable'
    current, _ = _module_fingerprint(kind)
    if not current:
        return True, 'nothing to fingerprint'
    if str(stamped.get('fingerprint', '')) != current:
        return False, ('the code that produced it has changed since (%s -> %s)'
                       % (str(stamped.get('fingerprint', '?'))[:8], current[:8]))
    stamped_corpus = str(stamped.get('corpus', ''))
    if c is not None and stamped_corpus:
        here_fp, here_label = corpus_fingerprint(c)
        if here_fp and here_fp != stamped_corpus:
            return False, ('it was built from a DIFFERENT corpus ("%s", not "%s") -- reusing it would '
                           'report that corpus\'s results as this one\'s'
                           % (str(stamped.get('corpus_label', '?')), here_label or '?'))
        if not here_fp:
            return True, 'this run\'s corpus could not be fingerprinted, so it was not checked'
    elif c is not None and not stamped_corpus:
        return True, 'no corpus recorded in the stamp, so which corpus produced it could not be checked'
    return True, ''


def _find_existing_parse_csv(c, must, required_columns, exclude=(), kind=''):
    """Shared cross-run reuse probe: [path] to a table already in the output dir (from a prior or KILLED
    run on THIS corpus) so a restart skips the slow re-parse; [] when nothing is trustworthy, so anything
    unexpected falls through to a fresh parse rather than risking wrong data.

      must              basename substrings ALL required, lowercase, e.g. ('svo', 'stanza')
      required_columns  columns the file must ACTUALLY have -- the real gate; a filename alone is not
                        evidence, and derived artifacts reuse the same words
      exclude           extra basename substrings to reject, on top of the standard list below

    The standard exclusions carry hard-won cases: derived artifacts share the parent's words AND often some
    of its columns (a by-doc frequency table has 'Object (O)'; a filtered SVO subset has every SVO column
    but only some rows), and a 'binned' copy can be LARGER than the real table -- 176MB vs 172MB for
    Harry Potter NER -- so 'largest wins' picks the wrong file without them.

    NOTE: the parsers write these tables when the parse COMPLETES, so a present, valid file means it
    finished. If a run is killed DURING a parse, delete the partial csv before re-running."""
    outdir = c.get('outputDir') or ''
    if not outdir or not os.path.isdir(outdir):
        return []
    import glob
    import pandas as pd
    # 'lemma' is here for a measured reason, not tidiness: a Stanza SVO run writes BOTH
    # NLP_SVO_Stanza_Dir_<corpus>.csv (0.23MB, the canonical table) and NLP_SVO_lemma_Stanza_Dir_<corpus>.csv
    # (0.24MB, a lemmatised variant) with IDENTICAL columns -- the variant is LARGER, so 'largest wins'
    # picks it without this. _find_existing_pos_csv already excluded it for the same reason.
    skip = ('binned', 'frequency', 'freq', 'chart', 'no_hyperlinks', 'group', 'bydoc', 'bysent',
            'stats', 'records', 'filter', 'lemma') + tuple(exclude)
    best, best_size = None, 0
    for p in glob.glob(os.path.join(outdir, '**', '*.csv'), recursive=True):
        b = os.path.basename(p).lower()
        if not all(m in b for m in must) or any(x in b for x in skip):
            continue
        try:
            head = pd.read_csv(p, nrows=5, encoding='utf-8', on_bad_lines='skip')
        except Exception:
            continue
        if head.empty or not all(col in head.columns for col in required_columns):
            continue
        try:
            size = os.path.getsize(p)
        except Exception:
            size = 0
        if size > best_size:
            best, best_size = p, size
    if not best:
        return []
    if kind:
        ok, why = provenance_is_current(best, kind, c)
        if not ok:
            print('>>> Corpus Profiler: NOT reusing %s -- %s. Re-running that analysis.'
                  % (os.path.basename(best), why))
            return []
        if why:
            print('>>> Corpus Profiler: reusing %s (%s)' % (os.path.basename(best), why))
    return [best]


def _find_existing_svo_csv(c):
    """[path] to this corpus's SVO table from a prior/killed run. Under a Stanza config SVO is the
    profiler's most expensive pass -- dependency parsing, hours on a large corpus -- and it had no reuse at
    all, so every interrupted sweep re-paid it in full. Tagged to the configured parser."""
    return _find_existing_parse_csv(c, ('svo', _configured_parser_tag(c)),
                                    ('Subject (S)', 'Verb (V)', 'Object (O)'), kind='svo')


def _find_existing_sentiment_csv(c):
    """[path] to this corpus's Stanza sentiment table from a prior/killed run (a second neural pass over
    every sentence -- hours on a large corpus). Tagged 'stanza' because _run_sentiment always uses Stanza
    with no dispatch: a CoreNLP sentiment table left by another tool must NOT be picked up."""
    return _find_existing_parse_csv(c, ('sentiment', 'stanza'),
                                    ('Sentiment score', 'Sentiment label'), kind='sentiment')


def _find_existing_srl_csv(c):
    """[path] to this corpus's SRL table from a prior/killed run. SRL is a heavy transformer pass in the
    isolated py3.8 env -- HOURS on a large corpus, and (unlike CoreNLP/POS/NER/SVO/sentiment) it was the ONE
    expensive pass with no reuse, so an interrupted sweep re-paid it in full. Signature: 'srl' in the name
    with the SRL output columns (Predicate + Frame + the ARG0 role), not a derived/frequency artifact."""
    return _find_existing_parse_csv(c, ('srl',), ('Predicate', 'Frame', 'ARG0 (Agent)'), kind='srl')


def _find_existing_ner_csv(c):
    """Return [path] to an NER table already in the output dir (from a prior/killed run on THIS corpus), so
    a restart can skip the slow NER re-parse -- Stanza NER is ~1h30m on Harry Potter, and unlike the CoreNLP
    and POS passes it had no reuse path, so every interrupted sweep re-paid it in full. [] if none is
    trustworthy, so anything unexpected falls through to a fresh parse.

    Gated like the POS reuse: a non-empty CSV whose basename carries 'ner' AND the CONFIGURED parser's tag,
    is not a derived artifact, and actually has an 'NER' column; largest wins (the full per-token table).
    Validation reads only the header (5 rows) -- cheap even beside a 172MB table.

    'binned' is excluded for a concrete reason: the binned copy carries 'ner' in its name and would
    otherwise be the LARGEST match, and _bin_numeric_columns_for_chart used to gut its text columns --
    reusing it would have resurrected destroyed data as if it were the parse."""
    outdir = c.get('outputDir') or ''
    if not outdir or not os.path.isdir(outdir):
        return []
    import glob
    import pandas as pd
    tag = _configured_parser_tag(c)
    best, best_size = None, 0
    for p in glob.glob(os.path.join(outdir, '**', '*.csv'), recursive=True):
        b = os.path.basename(p).lower()
        if 'ner' not in b or tag not in b:
            continue
        if any(x in b for x in ('binned', 'frequency', 'freq', 'chart', 'no_hyperlinks', 'group',
                                'bydoc', 'bysent', 'stats', 'gender', 'quote', 'svo', 'lemma')):
            continue
        try:
            head = pd.read_csv(p, nrows=5, encoding='utf-8', on_bad_lines='skip')
        except Exception:
            continue
        if head.empty or 'NER' not in head.columns:
            continue
        try:
            size = os.path.getsize(p)
        except Exception:
            size = 0
        if size > best_size:
            best, best_size = p, size
    return [best] if best else []


def _run_ner(c):
    """People, organizations, locations (NER) via the CONFIGURED parser -- CoreNLP only when the default
    NLP package IS CoreNLP (and installed), otherwise Stanza (default) or spaCy. No Java unless CoreNLP is
    the chosen parser. NER is parser-agnostic, so the profile's entities match the parser the user selected
    everywhere else in the Suite. Gender/dialogue/dates are NOT produced here (see _run_gender_dialogue_dates)."""
    # Reuse the shared combined-CoreNLP cache ONLY under a CoreNLP config -- under Stanza/spaCy we honor the
    # configured parser even if a CoreNLP enrichment pass also ran (it needs NER internally for coref/quote).
    if _is_corenlp_package(c.get('package')) and _corenlp_available():
        picked = _cache_pick_any(c.get('_corenlp_files'), 'corenlp_ner')
        if picked:
            print('>>> Entities/NER: used the shared CoreNLP cache -- no re-parse')
            return picked
    # A prior (or killed) run may already hold this corpus's NER table -- the parse is the slow part. Same
    # deal as the CoreNLP/POS reuse: a valid table in the output dir is reused instead of re-parsed. Checked
    # for EVERY parser, and matched against the configured one (see _find_existing_ner_csv).
    existing = _find_existing_ner_csv(c)
    if existing:
        print('>>> Entities/NER: reusing an existing %s NER table (%s) -- skipping the ~hour re-parse'
              % (_configured_parser_tag(c), os.path.basename(existing[0])))
        return list(dict.fromkeys(_files(existing)))
    # 'No charts' (NOT c['chartPackage']) -- the SAME rule as the POS pass below, for the same reason: the
    # profiler must never chart the RAW PER-TOKEN table. On Harry Potter this NER table is 1,414,910 rows /
    # 172MB; charting it exceeds Excel's 1,048,576-row cap, falls back to Plotly over 1.4M points, drags a
    # ~176MB binned copy and a groupBy stats pass behind it, and stalls the sweep for hours -- to render a
    # per-token scatter that means nothing. The profile builds its own NER charts from the by-document
    # frequency table, and _interp_ner reads the raw csv directly, so nothing of value is lost.
    if _is_corenlp_package(c.get('package')) and _corenlp_available():
        import Stanford_CoreNLP_util
        NER_list = ['PERSON', 'ORGANIZATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']
        print('>>> Entities/NER: Stanford CoreNLP (configured parser)')
        out = Stanford_CoreNLP_util.CoreNLP_annotate(
            c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
            'No charts', c['dataTransformation'], ['NER'], False,
            c['language'], c['export_json_var'], c['memory_var'],
            c['document_length_var'], c['limit_sentence_length_var'], NERs=NER_list)
        return _files(out)
    if 'spacy' in str(c.get('package', '')).lower():
        import spaCy_util
        print('>>> Entities/NER: spaCy (configured parser)')
        out = spaCy_util.spaCy_annotate(
            c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
            'No charts', c['dataTransformation'], 'NER', False,
            c['language'], c['memory_var'], c['document_length_var'], c['limit_sentence_length_var'])
        return list(dict.fromkeys(_files(out)))
    import Stanza_util
    print('>>> Entities/NER: Stanza (configured parser) -- no Java')
    out = Stanza_util.Stanza_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        'No charts', c['dataTransformation'], ['NER'], False,
        [c['language']], c['memory_var'], c['document_length_var'], c['limit_sentence_length_var'])
    return list(dict.fromkeys(_files(out)))   # Stanza returns the file once per doc; dedupe


def _run_gender_dialogue_dates(c):
    """Gender (coreference-based), dialogue/quotes and normalized dates -- the CoreNLP-ONLY enrichments (no
    Stanza/spaCy equivalent). Runs whenever CoreNLP + Java are installed, REGARDLESS of the configured parser
    (there is no Python alternative); returns [] with a note when they are not, and the summary tells the user
    how to enable them. Reads from the shared combined-CoreNLP cache if the parse phase produced it."""
    picked = _cache_pick_any(c.get('_corenlp_files'),
                             'corenlp_gender', 'corenlp_quote', 'corenlp_normalized-date')
    if picked:
        print('>>> Gender/dialogue/dates: used the shared CoreNLP cache (%d files) -- no re-parse' % len(picked))
        return picked
    if not _corenlp_available():
        print('>>> Gender/dialogue/dates: SKIPPED -- CoreNLP + Java not installed (CoreNLP-only features)')
        return []
    import Stanford_CoreNLP_util
    out = Stanford_CoreNLP_util.CoreNLP_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation'],
        ['gender', 'quote', 'normalized-date'], False,
        c['language'], c['export_json_var'], c['memory_var'],
        c['document_length_var'], c['limit_sentence_length_var'])
    return _files(out)


# ---- semantics (English + WordNet) --------------------------------------------------------
def _run_semantic_classes(c):
    # parse POS to noun/verb lemma lists, then aggregate them UP to THREE complementary knowledge bases:
    #   WordNet  -- top-synset classes for nouns AND verbs (the interpretable "people vs things" view)
    #   VerbNet  -- verb CLASSES (verbs only)
    #   FrameNet -- semantic FRAMES (verbs and nouns)
    # Same lemma lists, three lenses on meaning. Each aggregation is guarded so one failing (e.g. an
    # NLTK corpus not downloaded) never loses the others.
    import semantic_aggregation_WordNet_util
    import semantic_aggregation_util
    cp, dt = c['chartPackage'], c['dataTransformation']

    # POS noun/verb lemma lists come from a STANZA POS pass -- NO CoreNLP, NO Java. The WordNet /
    # VerbNet / FrameNet aggregators each read the FIRST column of a CSV as the lemma list (see
    # semantic_aggregation_util._read_word_list and semantic_aggregation_WordNet_util.aggregate_GoingUP),
    # so we split the Stanza 'All POS' table into a verb-lemma CSV and a noun-lemma CSV and feed those.
    # This is what lets Semantics run under any configured parser -- CoreNLP is NOT required for it.
    verb_file, noun_file = _stanza_pos_noun_verb_files(c)
    if verb_file or noun_file:
        print('>>> Semantics: noun/verb lemma lists from the Stanza POS pass (no CoreNLP)')

    out = []
    if not (verb_file or noun_file):
        return out

    # WordNet: nouns and verbs -> top-synset classes
    for f, tag in ((verb_file, 'VERB'), (noun_file, 'NOUN')):
        if not f:
            continue
        try:
            out += _files(semantic_aggregation_WordNet_util.aggregate_GoingUP(
                '', f, _analysis_dir(c, 'semantic_classes'), c['config_filename'], tag,
                False, cp, dt, c['language']))
        except Exception as e:
            print('Corpus Profiler: WordNet %s aggregation skipped: %s' % (tag, e))

    # VerbNet (verbs only) + FrameNet (verbs), then FrameNet (nouns)
    if verb_file:
        for agg, name in ((semantic_aggregation_util.aggregate_VerbNet, 'VerbNet'),
                          (semantic_aggregation_util.aggregate_FrameNet, 'FrameNet')):
            try:
                out += _files(agg(verb_file, _analysis_dir(c, 'semantic_classes'),
                                  'VERB', cp, dt))
            except Exception as e:
                print('Corpus Profiler: %s VERB aggregation skipped: %s' % (name, e))
    if noun_file:
        try:
            out += _files(semantic_aggregation_util.aggregate_FrameNet(
                noun_file, _analysis_dir(c, 'semantic_classes'), 'NOUN', cp, dt))
        except Exception as e:
            print('Corpus Profiler: FrameNet NOUN aggregation skipped: %s' % e)
    return out


# ---- semantics: BERT word embeddings -> interactive 2-D t-SNE semantic map (top-200 words, bounded) ----
def _run_embeddings(c):
    import BERT_util
    # signature: (window, inputFilename, inputDir, outputDir, openOutputFiles, chartPackage,
    #   dataTransformation, vis_menu_var, dim_menu_var, compute_distances_var, top_words_var,
    #   keywords_var, lemmatize_var, remove_stopwords_var, configFileName). Defaults mirror the
    #   Word2Vec GUI: plot vectors, 2-D t-SNE, top-200 words (bounded), lemmatize, drop stopwords.
    out = BERT_util.word_embeddings_BERT(
        c['window'], c['inputFilename'], c['inputDir'], _analysis_dir(c, 'embeddings'), False,
        c['chartPackage'], c['dataTransformation'],
        'Plot word vectors', '2D', False, 200, '', True, True, c['config_filename'])
    return _files(out)


def _find_existing_pos_csv(c):
    """Return [path] to a POS CoNLL table already in the output dir (from a prior/killed run on THIS
    corpus), so a restart can skip the slow Stanza POS re-parse; [] if none is trustworthy. Accepts only
    a CSV whose basename looks like the POS table (has 'pos' + 'stanza', not a chart / frequency / binned
    / by-doc / lemma-list file) AND that actually has a 'POS' column; picks the largest (the CoNLL table).
    Validation reads only the header (5 rows) -- cheap. NOTE: the table is written when the parse
    completes, so a present, valid file means POS finished; if you ever kill DURING the POS parse, delete
    the partial CSV before re-running."""
    outdir = c.get('outputDir') or ''
    if not outdir or not os.path.isdir(outdir):
        return []
    import glob
    import pandas as pd
    best, best_size = None, 0
    for p in glob.glob(os.path.join(outdir, '**', '*.csv'), recursive=True):
        b = os.path.basename(p).lower()
        if 'pos' not in b or 'stanza' not in b:
            continue
        if any(x in b for x in ('binned', 'frequency', 'chart', 'no_hyperlinks', 'group', 'bydoc',
                                'stats', 'lemma')):
            continue
        try:
            head = pd.read_csv(p, nrows=5, encoding='utf-8', on_bad_lines='skip')
        except Exception:
            continue
        if head.empty or 'POS' not in head.columns:
            continue
        try:
            size = os.path.getsize(p)
        except Exception:
            size = 0
        if size > best_size:
            best, best_size = p, size
    return [best] if best else []


# ---- syntax: parts-of-speech distribution (nouns, verbs, adjectives, adverbs, pronouns) via Stanza POS ----
def _run_pos_stats(c):
    # Reuse the shared Stanza POS pass if the parse-priming already ran it (Syntax + Semantics share
    # one POS parse -- see _prime_parse_cache). Otherwise parse now.
    cached = c.get('_stanza_pos_files')
    if cached:
        print('>>> Syntax/Semantics: reused the shared Stanza POS pass -- no re-parse')
        return list(dict.fromkeys(_files(cached)))
    # A prior (or killed) run may have already produced the POS CoNLL table for THIS corpus -- the parse
    # is the slow part (~1.5h on a large corpus). If a valid one is sitting in the output dir, REUSE it
    # instead of re-parsing. Gated + fail-safe: only a non-empty CSV that looks like the POS table AND
    # has a 'POS' column is accepted; anything off falls through to a fresh parse.
    existing = _find_existing_pos_csv(c)
    if existing:
        print('>>> Syntax/Semantics: reusing an existing Stanza POS table (%s) -- skipping the ~hour re-parse'
              % os.path.basename(existing[0]))
        return list(dict.fromkeys(_files(existing)))
    import Stanza_util
    # 'No charts' (NOT c['chartPackage']): the profiler must NOT chart the raw per-token POS CoNLL
    # table. On a large corpus that table exceeds Excel's 1,048,576-row limit (Harry Potter: >1M
    # tokens -> "Row numbers must be between 1 and 1048576") and a per-token table is meaningless as a
    # chart anyway. We need only the CSV; the summary builds its own compact POS-distribution chart from
    # the POS column (see _interp_syntax / the 'Parts of speech' spec in build_paper_summary).
    out = Stanza_util.Stanza_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        'No charts', c['dataTransformation'], ['All POS'], False,
        [c['language']], c['memory_var'], c['document_length_var'], c['limit_sentence_length_var'])
    return list(dict.fromkeys(_files(out)))   # Stanza returns the file once per doc; dedupe


def _stanza_pos_noun_verb_files(c):
    """From a Stanza POS pass (no Java), write two 1-column CSVs -- verb lemmas and noun lemmas -- in
    the first-column format the WordNet/VerbNet/FrameNet aggregators read (_read_word_list reads column
    0). Returns (verb_file, noun_file); either may be None. This removes the CoreNLP dependency from the
    Semantics knowledge-base aggregation."""
    import pandas as pd
    df = _find_pos_df(_run_pos_stats(c))   # reuses the shared Stanza POS pass when primed
    if df is None or 'POS' not in df.columns:
        return None, None
    # lemma column: prefer a real 'Lemma', fall back to the surface word/form
    lemcol = next((col for col in df.columns if str(col).strip().lower() == 'lemma'), None)
    have_real_lemma = lemcol is not None
    if lemcol is None:
        lemcol = next((col for col in df.columns if str(col).strip().lower() in ('word', 'form')), None)
    if lemcol is None:
        return None, None
    upos = df['POS'].astype(str).str.upper()

    # The Stanza POS pass is 'tokenize,pos' (no lemma), so when there's no real Lemma column, lemcol
    # holds the SURFACE form. Lemmatize it (English WordNet lemmatizer) so the WordNet/VerbNet/FrameNet
    # lookups match inflected words (ran->run, dogs->dog) -- otherwise VERB aggregation in particular
    # badly under-counts. Semantics KB aggregation is English-only, so WordNet is the right tool; falls
    # back to the surface form if WordNet isn't available.
    _lemmatizer = None
    if not have_real_lemma:
        try:
            from nltk.stem import WordNetLemmatizer
            _lemmatizer = WordNetLemmatizer()
            _lemmatizer.lemmatize('tests')   # force the WordNet corpus to load now; raises if absent
        except Exception:
            _lemmatizer = None

    def _lemmas(mask, wn_pos):
        s = df.loc[mask, lemcol].astype(str).str.strip().str.lower()
        words = {w for w in s if w and w != 'nan' and any(ch.isalpha() for ch in w)}
        if _lemmatizer is not None:
            lemmatized = set()
            for w in words:
                try:
                    lemmatized.add(_lemmatizer.lemmatize(w, wn_pos))
                except Exception:
                    lemmatized.add(w)
            words = lemmatized
        return sorted(words)

    verbs = _lemmas(upos == 'VERB', 'v')
    nouns = _lemmas(upos.isin(['NOUN', 'PROPN']), 'n')
    # beside the aggregations they feed, not in the profile folder: these are working files of the
    # semantic analysis, not results a reader opens
    _sem = _analysis_dir(c, 'semantic_classes')
    vpath = os.path.join(_sem, 'NLP_Stanza_POS_lemma_Verbs.csv')
    npath = os.path.join(_sem, 'NLP_Stanza_POS_lemma_Nouns.csv')
    if verbs:
        pd.DataFrame({'Word': verbs}).to_csv(vpath, index=False, encoding='utf-8')
    if nouns:
        pd.DataFrame({'Word': nouns}).to_csv(npath, index=False, encoding='utf-8')
    return (vpath if verbs else None), (npath if nouns else None)


def _is_corenlp_package(package):
    # True only when the user actually configured Stanford CoreNLP (or its OpenIE mode). Everything
    # else (Stanza, spaCy) is a Python parser -- the Suite's direction is to avoid Java/CoreNLP unless
    # strictly necessary (gender / dialogue / normalized dates are CoreNLP-only; SVO and POS are not).
    p = str(package).lower()
    return ('corenlp' in p) or ('stanford' in p) or ('openie' in p)


_CORENLP_AVAILABLE = None   # memoized per process (the user restarts between runs)


def _corenlp_available():
    """True iff BOTH Java and the Stanford CoreNLP engine are installed. When True the profiler USES
    CoreNLP for the CoreNLP-ONLY features (gender, dialogue/quotes, normalized dates) even if the
    configured parser is Stanza/spaCy -- there is no Python alternative for those. When False those
    features are skipped and the summary tells the user they need CoreNLP + Java and how to install
    them. Memoized: the check shells out to `java -version` and reads the external-software config once."""
    global _CORENLP_AVAILABLE
    if _CORENLP_AVAILABLE is not None:
        return _CORENLP_AVAILABLE
    ok = False
    try:
        import subprocess
        import IO_libraries_util
        jr = subprocess.run([IO_libraries_util.get_java_executable(), '-version'], capture_output=True)
        if jr.returncode == 0:
            for row in IO_libraries_util.get_existing_software_config()[1:]:   # skip header
                if len(row) >= 2 and 'corenlp' in str(row[0]).lower().replace(' ', ''):
                    d = str(row[1]).strip()
                    ok = bool(d) and os.path.isdir(d)
                    break
    except Exception:
        ok = False
    _CORENLP_AVAILABLE = ok
    print('>>> Corpus Profiler: Stanford CoreNLP + Java installed = %s '
          '(CoreNLP-only features -- gender, dialogue, normalized dates -- %s)'
          % (ok, 'will run' if ok else 'will be skipped'))
    return ok


# ---- narrative: SVO (via the CONFIGURED parser) + SRL (transformer; self-skips if env absent) ----
def _run_svo(c):
    # Subject-Verb-Object triples via the CONFIGURED parser -- SVO needs no Java. CoreNLP is used ONLY
    # when the user selected CoreNLP/OpenIE AND CoreNLP is actually installed (then we also reuse the
    # shared CoreNLP cache); otherwise SVO runs through Stanza (default) or spaCy -- so a CoreNLP config
    # on a machine WITHOUT CoreNLP falls back to Stanza instead of failing, since SVO is parser-agnostic.
    if _is_corenlp_package(c.get('package')) and _corenlp_available():
        picked = _cache_pick_any(c.get('_corenlp_files'), 'corenlp_svo')
        if picked:
            print('>>> Narrative/SVO: used the shared CoreNLP cache (%d files) -- no re-parse' % len(picked))
            return picked
    # A prior (or killed) run may already hold this corpus's SVO table. Under a Stanza config this is the
    # profiler's SINGLE most expensive pass -- dependency parsing, hours on a large corpus -- so it is the
    # one most worth never re-paying after a crash or power cut. Checked for EVERY parser, before any parse.
    existing = _find_existing_svo_csv(c)
    if existing:
        print('>>> Narrative/SVO: reusing an existing %s SVO table (%s) -- skipping the ~hours re-parse'
              % (_configured_parser_tag(c), os.path.basename(existing[0])))
        return list(dict.fromkeys(_files(existing)))
    if _is_corenlp_package(c.get('package')) and _corenlp_available():
        # 'No charts' (NOT c['chartPackage']): the SVO chart branch in parsers_annotators_visualization
        # tries to chart a 'Verb (V)' column on the CoNLL PARSE table (which has no such column) ->
        # KeyError 'Verb (V)' (Evan's crash). The profiler doesn't need those charts -- it builds its own
        # narrative summary from the SVO CSV -- so suppress them here for all three parsers.
        import Stanford_CoreNLP_util
        out = Stanford_CoreNLP_util.CoreNLP_annotate(
            c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
            'No charts', c['dataTransformation'], ['SVO'], False,
            c['language'], c['export_json_var'], c['memory_var'],
            c['document_length_var'], c['limit_sentence_length_var'])
        return _files(out)
    if 'spacy' in str(c.get('package', '')).lower():
        import spaCy_util
        out = spaCy_util.spaCy_annotate(
            c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
            'No charts', c['dataTransformation'], 'SVO', False,
            c['language'], c['memory_var'], c['document_length_var'], c['limit_sentence_length_var'])
        return _files(out)
    # default: Stanza -- the modern Python parser, no Java (same call shape as the sentiment runner)
    import Stanza_util
    out = Stanza_util.Stanza_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        'No charts', c['dataTransformation'], ['SVO'], False,
        [c['language']], c['memory_var'], c['document_length_var'], c['limit_sentence_length_var'])
    files = _files(out)
    stamp_provenance(files, 'svo', c)
    return files


def _run_srl(c):
    # SRL needs the isolated transformer-srl env + model; skip cleanly if not installed
    import SRL_util
    if not SRL_util.is_available():
        return []
    # A prior (or killed) run may already hold this corpus's SRL table. SRL is the heaviest pass with the
    # least feedback -- a transformer in an isolated py3.8 subprocess, HOURS on a large corpus, no progress
    # output -- and it was the last expensive pass without reuse, so an interruption re-paid it in full.
    existing = _find_existing_srl_csv(c)
    if existing:
        print('>>> Narrative/SRL: reusing an existing SRL table (%s) -- skipping the ~hours re-run'
              % os.path.basename(existing[0]))
        return list(dict.fromkeys(_files(existing)))
    import GUI_util
    files = _files(SRL_util.run_SRL(GUI_util.window, c['inputFilename'], c['inputDir'],
                                    c['outputDir'], c['chartPackage'], c['dataTransformation']))
    stamp_provenance(files, 'srl', c)
    return files


# ---- sentiment: Stanza neural sentiment (a real model, not a dictionary; already installed) ---
def _run_sentiment(c):
    # A prior (or killed) run may already hold this corpus's sentiment table -- a second neural pass over
    # EVERY sentence (~87k on Harry Potter), hours on a large corpus, and it had no reuse. Same deal as the
    # CoreNLP/POS/NER/SVO reuse: a valid table in the output dir is reused instead of re-parsed.
    existing = _find_existing_sentiment_csv(c)
    if existing:
        print('>>> Sentiment: reusing an existing Stanza sentiment table (%s) -- skipping the ~hours re-parse'
              % os.path.basename(existing[0]))
        return list(dict.fromkeys(_files(existing)))
    import Stanza_util
    out = Stanza_util.Stanza_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation'], ['sentiment'], False,
        [c['language']], c['memory_var'], c['document_length_var'], c['limit_sentence_length_var'])
    files = _files(out)
    # record WHICH CODE wrote this, so a later run can tell whether reusing it is still safe
    stamp_provenance(files, 'sentiment', c)
    return files


# ---- topics: Gensim LDA (pure Python). force=True bypasses the "needs 50+ files" advisory so the
#      unattended sweep can still run it; on a small corpus the topics are indicative, not authoritative. ---
def _run_topics(c):
    import topic_modeling_gensim_util
    return _files(topic_modeling_gensim_util.run_Gensim(
        c['window'], c['inputDir'], _analysis_dir(c, 'topics_Gensim'), c['config_filename'],
        10, True, True, False, False, False,
        c['chartPackage'], c['dataTransformation'], force=True))


# ---- character emotion arcs: Stanza NER + NRC's 8 emotions, traced per character across the story ---
def _run_character_arcs(c):
    import character_emotion_arcs_util
    # hand over the corpus's existing Stanza NER table if one is on disk: character_emotion_arcs otherwise
    # builds its OWN Stanza NER pipeline and re-parses the whole corpus (~1.5h). Deriving from the cached
    # table is seconds + the same NRC scoring. None -> it parses (its own progress print).
    _ner = _find_existing_ner_csv(c)
    return _files(character_emotion_arcs_util.main(
        c['inputFilename'], c['inputDir'], c['outputDir'], c['chartPackage'], c['dataTransformation'],
        conll_ner_table=(_ner[0] if _ner else None)))


# ---- character movement in space: Stanza tracks each character's locations -> animated migration map.
#      The map geocodes only DISTINCT locations (bounded); we further CAP to the 40 most frequent so an
#      unattended run on a big corpus can't stall on hundreds of Nominatim calls. ----
def _run_spatial_symbolic(c):
    """Actor-in-NON-geocodable-space events, from the CoNLL table the profile already has.

    The row is labelled "Where does it all happen? (geocodable AND symbolic space)", and symbolic
    space was a pointer at another GUI - so ticking it produced geocodable space and nothing else,
    while the label promised both. It runs here now, off the same parse everything else uses.

    BUILD, then everything BUILD is enough for.

    I first shipped only BUILD, on the grounds that the later steps need an actor ATTRIBUTE that is
    a research decision. That was wrong twice over. BUILD fills in actor_type itself, from the
    social-actor typology - the column is there when it finishes. And MOVEMENT needs no attribute at
    all: it needs a place and an order, which are space_type and Sentence ID, both in the table it
    just wrote. So a sweep that stopped at BUILD left the user with a csv and no way to see it.

    Movement (transitions, graph, interactive timeline) runs. The attribute x space cross-tab runs
    too, since actor_type exists - with the share of unclassified actors REPORTED, because proper
    names are deliberately never guessed at, so a corpus of named characters leaves most events
    unclassified and a cross-tab that does not say so would read as a finding about nobody.
    """
    conll = _find_existing_parse_csv(c, ('conll',),
                                     ('Form', 'Lemma', 'POS', 'Head'), kind='')
    if not conll:
        # Said loudly, because a silent [] here is what made this look like it had run: 0 files, no
        # error, and a summary reporting only geocodable space.
        print('>>> Symbolic space: NOT RUN -- it reads a CoNLL dependency table and there is none '
              'in this profile. Tick "Who did what to whom? (Narrative)", which writes one, and '
              'run again; or build it from the Symbolic Space GUI against an existing CoNLL table.')
        return []
    import GIS_symbolic_util as ss
    outdir = _analysis_dir(c, 'GIS', 'symbolic')
    events_csv, dropped = ss.extract_actor_space_events(conll[0], outdir)
    if not events_csv:
        print('>>> Symbolic space: the CoNLL table produced no actor-in-space events.')
        return []
    # Never silently: a corpus that tells its story with "he" and "they" can lose most of its
    # events here, and a thin table would otherwise read as a corpus with little movement in it.
    if dropped:
        print('>>> Symbolic space: %d event(s) dropped because the actor was a PRONOUN. Run '
              'coreference resolution first to recover them.' % dropped)
    out = _files(events_csv)

    try:
        import pandas as pd
        df = pd.read_csv(events_csv, encoding='utf-8-sig', on_bad_lines='skip')
    except Exception as e:
        print('Corpus Profiler: symbolic events written but not readable back (%s)' % e)
        return out
    if 'space_type' not in df.columns or df.empty:
        return out

    # ---- movement: needs a place and an order, nothing chosen by anybody --------------------
    try:
        import GIS_symbolic_util as ss
        seq_col = 'Sentence ID' if 'Sentence ID' in df.columns else None
        d = df.sort_values([c for c in ('Document ID', seq_col) if c]) if seq_col else df
        sequence = [str(x) for x in d['space_type'].tolist() if str(x).strip()]
        if len(sequence) > 1:
            # classify=False: these are already space CATEGORIES (BUILD classified them). Left at
            # the default they are re-classified as raw place nouns, 'domestic_interior' matches
            # nothing, and the result is zero transitions from 5,228 events.
            _path, edges = ss.narrative_transitions(sequence, classify=False)
            trans_csv = os.path.join(outdir, 'symbolic_space_transitions.csv')
            pd.DataFrame(edges, columns=['from', 'to', 'count']).to_csv(
                trans_csv, index=False, encoding='utf-8-sig')
            out += [trans_csv]
            png = os.path.join(outdir, 'symbolic_space_movement.png')
            ss.plot_transition_graph(edges, png)
            if os.path.isfile(png):
                out += [png]
        timeline = ss.symbolic_movement_timeline(events_csv, outdir, location_col='space_type')
        if timeline:
            out += _files(timeline)
    except Exception as e:
        print('Corpus Profiler: symbolic movement skipped (%s)' % e)

    # ---- actor type x space, with the unclassified share said out loud ----------------------
    try:
        if 'actor_type' in df.columns:
            types = df['actor_type'].astype(str).str.strip().str.lower()
            unclassified = int((types.isin(('', 'nan', 'unclassified'))).sum())
            share = 100.0 * unclassified / max(len(df), 1)
            print('>>> Symbolic space: %d of %d events (%.0f%%) have an UNCLASSIFIED actor - the '
                  'typology never guesses at proper names, so named characters land here. The '
                  'cross-tab describes the remaining %.0f%%.'
                  % (unclassified, len(df), share, 100.0 - share))
            # (attribute, category) PAIRS, already classified - not a DataFrame, and not raw nouns
            pairs = list(zip(df['actor_type'].astype(str), df['space_type'].astype(str)))
            table = ss.attribute_space_crosstab(pairs, classify=False)
            csv_out = os.path.join(outdir, 'symbolic_space_actor_type_x_space.csv')
            stats = ss.crosstab_stats(table)
            ss.save_crosstab_csv(table, csv_out, stats=stats)
            out += [csv_out]
            heat = os.path.join(outdir, 'symbolic_space_actor_type_x_space_heatmap.png')
            ss.plot_attribute_space_heatmap(table, heat, stats=stats)
            if os.path.isfile(heat):
                out += [heat]
    except Exception as e:
        print('Corpus Profiler: symbolic distribution skipped (%s)' % e)

    return [f for f in out if f]


def _run_character_movement(c):
    import charts_util
    files = list(c.get('_ner_track_files') or [])   # shared NER location pass, if the parse phase primed it
    if files:
        print('>>> Characters/movement: used the shared NER location cache -- no re-parse')
    else:
        import NER_location_tracking_util
        files = _files(NER_location_tracking_util.main(
            c['inputFilename'], c['inputDir'], _analysis_dir(c, 'GIS', 'geocodable'),
            c['chartPackage'], c['dataTransformation']))
    csvs = [f for f in files if str(f).lower().endswith('.csv')]
    if not csvs:
        return files
    track_csv = csvs[0]
    map_dir = os.path.dirname(track_csv)
    map_input = track_csv
    try:
        import pandas as pd
        df = pd.read_csv(track_csv)
        if 'Location' in df.columns and df['Location'].nunique() > 40:
            top_locs = df['Location'].value_counts().head(40).index
            capped = os.path.join(map_dir, 'NLP_character_movement_top40_locations.csv')
            df[df['Location'].isin(top_locs)].to_csv(capped, index=False, encoding='utf-8')
            map_input = capped
            files.append(capped)
    except Exception:
        pass
    try:
        # order the animation by narrative time (Sentence ID), with a per-document filter -> movement
        # in TIME and space, not merely space.
        files += _files(charts_util.animated_migration_map(
            map_input, map_dir, 'Entity', 'Location', sequence_col='Sentence ID', doc_col='Document'))
    except Exception as e:
        print('Corpus Profiler: character movement map skipped: %s' % e)
    return files


# ---- spatial: a QUICK geocodable-space snapshot -- a proportional-symbol map of the corpus's place
#      names. Locations come from the same Stanza NER pass Characters/movement uses; only the top-40
#      DISTINCT places are geocoded (bounded, so an unattended run can't stall). Geocoder: Google IF a
#      geocode API key is configured, else Nominatim/folium (no key, no download). The GIS GUI still
#      offers the full control (geocoder choice, Google Earth / folium / distances, manual review) --
#      this is the quick snapshot. ----
def _run_spatial_map(c):
    import charts_util
    files = list(c.get('_ner_track_files') or [])   # shared NER location pass, if the parse phase primed it
    if files:
        print('>>> Spatial: used the shared NER location cache -- no re-parse')
    else:
        import NER_location_tracking_util
        files = _files(NER_location_tracking_util.main(
            c['inputFilename'], c['inputDir'], _analysis_dir(c, 'GIS', 'geocodable'),
            c['chartPackage'], c['dataTransformation']))
    csvs = [f for f in files if str(f).lower().endswith('.csv')]
    if not csvs:
        return files
    track_csv = csvs[0]
    # Detect a configured Google geocode key by reading its config file DIRECTLY -- we must NOT call
    # GIS_pipeline_util.getGoogleAPIkey here because, when the key is missing, it pops an interactive
    # dialog (offering to open the TIPS file), which would hang the unattended profile. No file =
    # no key = Nominatim, silently.
    google_api = ''
    try:
        import GUI_IO_util
        cfg = os.path.join(GUI_IO_util.configPath, 'Google-geocode-API_config.csv')
        if os.path.isfile(cfg):
            with open(cfg, encoding='utf-8', errors='ignore') as fh:
                google_api = fh.read().strip()
    except Exception:
        google_api = ''
    try:
        map_file = charts_util.proportional_circle_map(
            track_csv, os.path.dirname(track_csv), 'Location', Google_API=google_api, top_n=40)
        if map_file:
            files.append(map_file)
    except Exception as e:
        print('Corpus Profiler: geocodable-space map skipped: %s' % e)
    return files


# ---------------------------------------------------------------------------------------------
# The registry.  id -> dict(category, label, kind, run)
#   kind == 'batch' -> run(c) invoked during a profile; 'gui' -> surfaced as an "open tool" link.
# ---------------------------------------------------------------------------------------------
REGISTRY = {
    # --- counts ---
    'statistics':       dict(category='counts', kind='batch', run=_run_statistics,
                             label='Statistics (sentences, words, syllables)'),
    'ngrams':           dict(category='counts', kind='batch', run=_run_ngrams,
                             label='N-grams'),
    'sentence_length':  dict(category='counts', kind='batch', run=_run_sentence_length,
                             label='Sentence length'),
    # 'line_length' dropped from the profiler: line length in prose is a typesetting artifact, not a
    # stylistic signal (meaningful only for poetry/lyrics -> use the standalone Style Analysis GUI).
    # --- vocabulary (a curated SNAPSHOT; the full ~20-option menu lives in the Style Analysis GUI,
    #     which the report/help points to). Sourced from style_analysis_main.run(). ---
    'yule':             dict(category='counts', kind='batch', run=_run_yule,
                             label="Vocabulary richness (word type/token ratio or Yule's K)"),
    'lexical_diversity': dict(category='counts', kind='batch', run=_run_lexical_diversity,
                             label='Lexical diversity (TTR, MTLD, vocd-D)'),
    'word_frequency':   dict(category='counts', kind='batch', run=_run_word_frequency,
                             label="Word frequency distribution (Zipf's Law)"),
    'tfidf':            dict(category='counts', kind='batch', run=_run_tfidf,
                             label='TF-IDF (most distinctive words per document)'),
    # 'hapax' dropped from the profiler: it re-tokenized the WHOLE corpus a SECOND time (its own n-gram
    # pass) purely to list once-occurring words -- which the N-grams analysis already emits as a hapax
    # file from its 1-gram results. Removing it halves the n-gram work (was "N-grams runs twice").
    'unusual_words':    dict(category='counts', kind='batch', run=_run_unusual_words,
                             label='Unusual words (via NLTK)'),
    'abstract_concrete': dict(category='counts', kind='batch', run=_run_abstract_concrete,
                             label='Abstract / concrete vocabulary'),
    'iconic':           dict(category='counts', kind='batch', run=_run_iconic,
                             label='Iconic vocabulary'),
    'capital_words':    dict(category='counts', kind='batch', run=_run_word_shape('capital'),
                             label='Capital-initial words'),
    # 'language_detection' dropped from the profiler: THREE detectors over EVERY file (slow on a large
    # corpus) to re-confirm the language already declared in the I/O config, and no interpreter read its
    # output -- it produced no finding. Still available on its own: menu "Language detection".
    # NER lives in COUNTS: people/organizations/locations are a basic descriptive extraction, run with the
    # user's CONFIGURED parser (Stanza/spaCy/CoreNLP) -- no Java unless CoreNLP is the chosen parser.
    'ner':              dict(category='counts', kind='batch', run=_run_ner,
                             label='People, organizations, locations (NER)'),
    # --- entities: the CoreNLP-ONLY enrichments (gender, dialogue/quotes, normalized dates). Availability-
    #     driven -- uses CoreNLP whenever installed, regardless of the configured parser; skipped otherwise. ---
    'gender_dialogue_dates': dict(category='entities', kind='batch', run=_run_gender_dialogue_dates,
                             label='Gender, dates, dialogue (via CoreNLP)'),
    # --- spatial: a quick geocodable-space snapshot RUNS in batch (proportional-symbol map; Google if a
    #     geocode key is configured, else Nominatim/folium). Full control (geocoder choice, API key,
    #     Google Earth / folium / distances, manual review) stays in the GIS GUI; symbolic space its GUI. ---
    'spatial_map':      dict(category='spatial', kind='batch', run=_run_spatial_map,
                             label='Geocodable space — proportional-symbol map of corpus locations (Nominatim/Google)'),
    'spatial_gis':      dict(category='spatial', kind='gui', gui_script='GIS_main.py',
                             label='Full geocoding & mapping — geocoder choice, API key, Google Earth / folium / distances  (opens GIS GUI)'),
    'spatial_symbolic': dict(category='spatial', kind='batch', run=_run_spatial_symbolic,
                             label='Symbolic space — actors in NON-geocodable space (house, field, forest, threshold)'),
    'spatial_symbolic_more': dict(category='spatial', kind='gui', gui_script='GIS_symbolic_main.py',
                             label='Symbolic space: distribution & movement — needs an actor attribute you choose  (opens Symbolic Space GUI)'),
    # --- semantics (snapshot: WordNet noun/verb classes; deeper tools via the Semantic GUI) ---
    'semantic_classes': dict(category='semantics', kind='batch', run=_run_semantic_classes,
                             label='Noun & verb classes (WordNet top synsets)'),
    'semantic_embeddings': dict(category='semantics', kind='batch', run=_run_embeddings,
                             label='Word embeddings (BERT) — interactive 2-D t-SNE semantic map'),
    'semantics_more':   dict(category='semantics', kind='gui', gui_script='semantic_analysis_main.py',
                             label='WSD · semantic similarity · nominalization  (opens Semantic Analysis GUI)'),
    # --- syntax: parts-of-speech distribution RUNS in batch (Stanza POS); deeper CoNLL analyses via GUI ---
    'syntax_pos':       dict(category='syntax', kind='batch', run=_run_pos_stats,
                             label='Parts of speech — nouns, verbs, adjectives, adverbs, pronouns (Stanza POS)'),
    'syntax_more':      dict(category='syntax', kind='gui', gui_script='CoNLL_table_analyzer_main.py',
                             label='Dependency · clause · function words · complexity · readability  (opens CoNLL Analyzer)'),
    # --- topics (Gensim LDA runs in batch, force-bypassing the 50-file advisory; deeper engines via GUI) ---
    'topics_gensim':    dict(category='topics', kind='batch', run=_run_topics,
                             label='Topic modeling (Gensim LDA)'),
    'topics_more':      dict(category='topics', kind='gui', gui_script='topic_modeling_main.py',
                             label='BERTopic · MALLET · coherence tuning  (opens Topic Modeling GUI)'),
    # --- narrative (SVO runs via CoreNLP; SRL via its transformer env, skipped if not installed) ---
    'narrative_svo':    dict(category='narrative', kind='batch', run=_run_svo,
                             label='SVO (Subject-Verb-Object)'),
    'narrative_srl':    dict(category='narrative', kind='batch', run=_run_srl,
                             label='SRL (Semantic Role Labeling)'),
    'narrative_more':   dict(category='narrative', kind='gui', gui_script='SVO_main.py',
                             label='Coreference · 5 Ws  (opens SVO GUI)'),
    # --- sentiment (VADER runs by default; other engines open from the Sentiment GUI) ---
    'sentiment_stanza': dict(category='sentiment', kind='batch', run=_run_sentiment,
                             label='Sentiment (Stanza)'),
    'sentiment_more':   dict(category='sentiment', kind='gui', gui_script='sentiment_analysis_main.py',
                             label='BERT · spaCy · VADER · NRC · SentiWordNet  (opens Sentiment GUI)'),
    # --- characters (a character-centric lens: emotional arcs + movement in space; both batch, Stanza-based) ---
    # Batch-only dimension -- no GUI pointer. (Whole-narrative "shape of stories" is heavy BERT+clustering
    # and GUI-coupled, like topics; it stays in the Sentiment GUI and is mentioned in this row's HELP.)
    'character_arcs':     dict(category='characters', kind='batch', run=_run_character_arcs,
                             label='Emotion arcs (NRC 8 emotions, per character across the story)'),
    'character_movement': dict(category='characters', kind='batch', run=_run_character_movement,
                             label='Movement in time & space (each character’s places over the story, mapped)'),
}


def analyses_in_category(category):
    return [aid for aid in REGISTRY if REGISTRY[aid]['category'] == category]


# ---------------------------------------------------------------------------------------------
# run_profile: execute the selected analyses, collect their output files.
#   ctx        shared args (window, inputFilename, inputDir, outputDir, config_filename,
#              chartPackage, dataTransformation, language, export_json_var, memory_var,
#              document_length_var, limit_sentence_length_var, ...)
#   selected   list of analysis ids to run (already expanded from the GUI '*' menus)
# Returns a `results` list of dicts: {id, category, label, kind, files, error}
# ---------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
# Shared PARSE CACHE. Each parser-dependent dimension used to launch its OWN full parse of the
# corpus, so a battery re-parsed all files ~8 times (CoreNLP/Java is the slow one). Parse ONCE per
# parser up front and let the dimensions read the cached annotations:
#   * ONE combined CoreNLP pass (NER + gender + quote + normalized-date + POS + SVO) replaces up to
#     three, routed to Entities / Semantics / Narrative by output filename.
#   * ONE NER location-tracking pass shared by Spatial and Characters-movement.
# Best-effort: on any failure a cache stays empty and the dimension falls back to its own parse, so
# this can never make a run less correct -- only faster. (Stanza can't combine annotators in one call,
# so POS/sentiment stay separate; the big win is folding the 3 CoreNLP passes into 1.)
# ---------------------------------------------------------------------------------------------
def _cache_pick(files, *substrs, exclude=()):
    """Cached files whose basename contains ALL substrs and none of exclude (case-insensitive)."""
    out = []
    for f in files or []:
        b = os.path.basename(str(f)).lower()
        if all(s.lower() in b for s in substrs) and not any(x.lower() in b for x in exclude):
            out.append(f)
    return out


def _cache_pick_any(files, *substrs):
    """Cached files whose basename contains ANY of substrs (case-insensitive)."""
    out = []
    for f in files or []:
        b = os.path.basename(str(f)).lower()
        if any(s.lower() in b for s in substrs):
            out.append(f)
    return out


def _find_existing_corenlp_files(ctx):
    """Return CoreNLP output files already in the output dir (from a prior/killed run on THIS corpus),
    so a restart can skip the slow combined CoreNLP enrichment pass (gender/quote/date -- HOURS on a large
    corpus). [] unless BOTH a gender output and a normalized-date output are present -- the enrichment pass's
    signature outputs, always produced together -- so a partial/failed prior pass isn't reused. (NER is NOT
    part of the signature: under a Stanza/spaCy config it's parsed separately and this pass has no NER file.)
    Like the POS reuse, these appear when the pass completes; if you kill DURING it, delete its output
    subdirs before re-running."""
    outdir = ctx.get('outputDir') or ''
    if not outdir or not os.path.isdir(outdir):
        return []
    import glob
    found = []
    for p in glob.glob(os.path.join(outdir, '**', '*.csv'), recursive=True):
        b = os.path.basename(p).lower()
        if 'corenlp' in b and any(k in b for k in ('ner', 'gender', 'quote', 'normalized-date', 'svo')):
            found.append(p)
    has_gender = any('gender' in os.path.basename(f).lower() for f in found)
    has_date = any('normalized-date' in os.path.basename(f).lower() for f in found)
    return found if (has_gender and has_date) else []


def corenlp_pass_reusable(outputDir):
    """True when a COMPLETED CoreNLP enrichment pass is already sitting in `outputDir` -- i.e. the slow Java
    pass will be REUSED rather than re-run (the user kept the folder at setup_profile_output_dir). Callers use
    this to avoid warning about hours that will NOT be spent."""
    return bool(_find_existing_corenlp_files({'outputDir': outputDir}))


def _reusable_artifacts(target_dir):
    """Human-readable labels for the expensive-to-recompute results already in `target_dir` that the profiler
    can REUSE on a re-run: a completed CoreNLP enrichment pass (gender + normalized-date) and/or a Stanza POS
    table. [] when none are present (so the caller falls back to the plain replace prompt)."""
    ctx = {'outputDir': target_dir}
    labels = []
    try:
        if _find_existing_corenlp_files(ctx):
            labels.append('a completed Stanford CoreNLP pass (gender / dialogue / dates) — hours to recompute')
    except Exception:
        pass
    try:
        if _find_existing_pos_csv(ctx):
            labels.append('a Stanza parts-of-speech table — up to ~an hour to recompute')
    except Exception:
        pass
    return labels


def setup_profile_output_dir(window, inputFilename, inputDir, outputDir):
    """Create the profiler's corpus_profile_<name> output dir. If a prior folder exists AND holds results the
    profiler can REUSE (a completed CoreNLP enrichment pass and/or a Stanza POS table -- each HOURS to recompute
    on a large corpus), first offer to KEEP them and reuse IN PLACE instead of the blanket wipe -- so the user
    needn't hunt for the right folder to preserve. Declining -> the standard 'will be replaced?' confirm (which
    still allows abort). Returns the dir path, or '' if the user declined. (Reuse-in-place: each analysis still
    refreshes its own outputs as it runs; leftover files from analyses no longer selected simply remain.)"""
    import IO_files_util
    import tkinter.messagebox as mb   # resolves the NLP_SILENT patch at call time, like the rest of the Suite
    # mirror make_output_subdirectory's exact naming for label='corpus_profile' so we probe the SAME folder
    if inputFilename:
        target = os.path.join(outputDir, 'corpus_profile_' + os.path.basename(inputFilename)[0:-4])
    elif inputDir:
        target = os.path.join(outputDir, 'corpus_profile_' + os.path.basename(inputDir))
    else:
        target = os.path.join(outputDir, 'corpus_profile')
    if os.path.isdir(target):
        reusable = _reusable_artifacts(target)
        if reusable and mb.askyesno(
                'Reuse existing results?',
                'This profile folder already exists and contains results the Corpus Profiler can REUSE, '
                'skipping potentially HOURS of re-parsing:\n\n  - ' + '\n  - '.join(reusable) + '\n\n'
                + target + '\n\nKeep these and reuse them?\n\n'
                'Yes = keep & reuse (each analysis still refreshes its own outputs as it runs)\n'
                'No = replace the whole folder and recompute everything',
                default='yes'):
            print('>>> Corpus Profiler: reusing the existing profile folder -- kept %s' % '; '.join(reusable))
            return target
    # nothing reusable, or the user chose to replace: standard create-with-replace-confirm (allows abort)
    return IO_files_util.make_output_subdirectory(inputFilename, inputDir, outputDir,
                                                  label='corpus_profile', silent=False)


def _prime_parse_cache(ctx, selected):
    ctx['_corenlp_files'] = None
    ctx['_ner_track_files'] = None
    sel = set(selected)

    # one combined CoreNLP pass covering every selected CoreNLP dimension. The gender/dialogue/dates
    # enrichments are added whenever CoreNLP + Java are INSTALLED -- auto-used even under a Stanza/spaCy
    # config, since there's no Python alternative. NER, by contrast, honors the CONFIGURED parser: it rides
    # this pass ONLY when the enrichments run (coref/quote need NER internally, so extracting it is free and
    # keeps the reuse signature) OR when CoreNLP is the chosen parser; under a Stanza/spaCy config _run_ner
    # parses NER itself and ignores this pass's NER. SVO likewise rides only under a CoreNLP config. If
    # CoreNLP isn't installed, nothing is added and each runner degrades on its own (NER -> configured
    # parser; gender/dialogue/dates -> skipped; the summary tells the user how to install CoreNLP).
    annotators = []
    _corenlp = _corenlp_available()
    _default_is_corenlp = _is_corenlp_package(ctx.get('package'))
    if _corenlp:
        if 'gender_dialogue_dates' in sel:
            annotators += ['gender', 'quote', 'normalized-date']
        # NER rides this pass ONLY when CoreNLP is the CONFIGURED parser (it's then the intended NER source,
        # a free rider on the enrichment parse). Under a Stanza/spaCy config, _run_ner parses NER with that
        # parser instead, so we do NOT run CoreNLP's NER annotator here -- entities stay on the chosen parser.
        if 'ner' in sel and _default_is_corenlp:
            annotators = ['NER'] + annotators
        if 'narrative_svo' in sel and _default_is_corenlp:
            annotators += ['SVO']
        # NOTE: Semantics POS is NOT taken from CoreNLP anymore -- it derives its noun/verb lemma lists
        # from the shared Stanza POS pass below, so it works with no Java regardless of CoreNLP.
    if len(annotators) >= 2:   # only worth combining when 2+ CoreNLP dimensions are on
        # REUSE: a prior run on this corpus may already have produced the CoreNLP outputs -- and that
        # pass is the single slowest step (Java NER/gender/quote/date, ~hours on Harry Potter). If a
        # completed set is in the output dir, reuse it instead of re-parsing (mirrors the POS reuse).
        existing = _find_existing_corenlp_files(ctx)
        if existing:
            print('>>> Corpus Profiler: reusing an existing CoreNLP pass (%d files) -- skipping the '
                  '~hours re-parse' % len(existing))
            ctx['_corenlp_files'] = existing
        else:
            try:
                import Stanford_CoreNLP_util
                NER_list = ['PERSON', 'ORGANIZATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']
                print('>>> Corpus Profiler: ONE combined CoreNLP pass for [%s] (replacing separate passes)'
                      % ', '.join(annotators))
                files = _files(Stanford_CoreNLP_util.CoreNLP_annotate(
                    ctx['config_filename'], ctx['inputFilename'], ctx['inputDir'], ctx['outputDir'], False,
                    ctx['chartPackage'], ctx['dataTransformation'], annotators, False,
                    ctx['language'], ctx['export_json_var'], ctx['memory_var'],
                    ctx['document_length_var'], ctx['limit_sentence_length_var'], NERs=NER_list))
                ctx['_corenlp_files'] = files
                print('>>> Corpus Profiler: combined CoreNLP pass cached %d output files' % len(files))
            except Exception as e:
                print('Corpus Profiler: combined CoreNLP pass failed (%s); dimensions will parse individually' % e)
                ctx['_corenlp_files'] = None

    # one shared STANZA POS pass (no Java) for Syntax (POS distribution) AND Semantics (noun/verb
    # knowledge-base aggregation derives its lemma lists from it). Parse the corpus for POS ONCE and
    # reuse -- a big win on a large corpus (Harry Potter POS is ~1h) versus parsing it twice.
    ctx['_stanza_pos_files'] = None
    if ('syntax_pos' in sel) or ('semantic_classes' in sel):
        have = reusable_from_manifest(ctx, 'syntax_pos', ctx.get('_previous'), ctx.get('_corpus_ok'))
        if have:
            print('>>> Corpus Profiler: reusing the shared Stanza POS pass from a previous run '
                  '(%d files) -- skipping the ~hour re-parse' % len(have))
            ctx['_stanza_pos_files'] = have
        else:
            try:
                print('>>> Corpus Profiler: ONE shared Stanza POS pass for Syntax + Semantics')
                ctx['_stanza_pos_files'] = _run_pos_stats(ctx)
            except Exception as e:
                print('Corpus Profiler: shared Stanza POS pass failed (%s); dimensions will parse individually' % e)
                ctx['_stanza_pos_files'] = None

    # one NER location-tracking pass shared by Spatial + Characters-movement (was run twice)
    if ('spatial_map' in sel) or ('character_movement' in sel):
        # the same table serves both, so either analysis's record can supply it
        have = (reusable_from_manifest(ctx, 'spatial_map', ctx.get('_previous'), ctx.get('_corpus_ok'))
                or reusable_from_manifest(ctx, 'character_movement', ctx.get('_previous'),
                                          ctx.get('_corpus_ok')))
        if have:
            print('>>> Corpus Profiler: reusing the shared NER location pass from a previous run '
                  '(%d files) -- no re-parse' % len(have))
            ctx['_ner_track_files'] = have
            return
        try:
            import NER_location_tracking_util
            print('>>> Corpus Profiler: ONE NER location pass shared by Spatial + Characters-movement')
            # its own folder, shared by both dimensions: the tracking table, the location summary
            # and the maps were four loose files in the profile folder. Both runners derive their
            # map directory from this table's path, so they follow it here.
            ctx['_ner_track_files'] = _files(NER_location_tracking_util.main(
                ctx['inputFilename'], ctx['inputDir'], _analysis_dir(ctx, 'GIS', 'geocodable'),
                ctx['chartPackage'], ctx['dataTransformation']))
        except Exception as e:
            print('Corpus Profiler: shared NER location pass failed (%s); dimensions will parse individually' % e)
            ctx['_ner_track_files'] = None


def run_profile(ctx, selected):
    import time as _time
    import IO_user_interface_util

    # Work out what can be reused BEFORE priming the parse cache. The shared passes in
    # _prime_parse_cache run ahead of the analysis loop and used to re-parse regardless: a re-run
    # skipped all 23 analyses and then spent an hour on a Stanza POS pass and an NER location pass
    # feeding analyses it had just decided not to run. Reuse in the loop alone does not reach them.
    _outputDir = ctx.get('outputDir') or ''
    _previous = load_manifest(_outputDir)
    _corpus_ok = False
    if _previous:
        _man_fp, _man_label = manifest_corpus(_outputDir)
        _here_fp, _here_label = corpus_fingerprint(ctx)
        if _man_fp and _here_fp:
            _corpus_ok = (_man_fp == _here_fp)
            if not _corpus_ok:
                print('>>> Corpus Profiler: the profile already in this folder was built from a '
                      'DIFFERENT corpus ("%s", not "%s"). Nothing from it is reused.'
                      % (_man_label or '?', _here_label or '?'))
        elif not _man_fp:
            _corpus_ok = True
            print('>>> Corpus Profiler: the existing profile records no corpus (written by an '
                  'earlier version); reusing it on the strength of the output folder.')
    ctx['_previous'] = _previous
    ctx['_corpus_ok'] = _corpus_ok

    _prime_parse_cache(ctx, selected)   # parse once, cache; runners read the cache (or fall back)
    results = []
    # UNIFORM per-analysis progress: some runners print their own "Started/Finished ... taking X" (the
    # parser utils via timed_alert), others print nothing -- so the log was inconsistent and a stalled
    # analysis was invisible (an analysis that never prints "Finished" is exactly where a hang is). Bracket
    # EVERY analysis here with the same wording the rest of the suite uses, plus an (i of N) counter for the
    # long unattended run.
    # ORDER: symbolic space reads a CoNLL dependency table, and the analysis that WRITES one is SVO,
    # under 'narrative' - which CATEGORY_ORDER puts after 'spatial'. So on a fresh corpus symbolic
    # space ran first, found no CoNLL table, and returned nothing: 0 files, no error, no folder, and
    # a summary section that said symbolic space "was considered". It only appeared to work on a
    # corpus profiled before, where a CoNLL table was already on disk from the earlier run.
    # Moved after its input rather than reordered wholesale, so every other category keeps its place.
    selected = list(selected)
    if 'spatial_symbolic' in selected and 'narrative_svo' in selected:
        if selected.index('spatial_symbolic') < selected.index('narrative_svo'):
            selected.remove('spatial_symbolic')
            selected.insert(selected.index('narrative_svo') + 1, 'spatial_symbolic')

    _batch = [a for a in selected if REGISTRY.get(a, {}).get('kind') == 'batch']
    _n, _done = len(_batch), 0

    # EVERY analysis reuses what a previous run of THIS corpus already produced, from one rule -
    # see reusable_from_manifest. Decided once here rather than per analysis: whether the manifest
    # describes the corpus in front of us is a property of the run, and fingerprinting the corpus
    # 23 times would read the whole input directory 23 times.
    _outputDir = ctx.get('outputDir') or ''
    _previous = load_manifest(_outputDir)
    _corpus_ok = False
    if _previous:
        _man_fp, _man_label = manifest_corpus(_outputDir)
        _here_fp, _here_label = corpus_fingerprint(ctx)
        if _man_fp and _here_fp:
            _corpus_ok = (_man_fp == _here_fp)
            if not _corpus_ok:
                print('>>> Corpus Profiler: the profile already in this folder was built from a '
                      'DIFFERENT corpus ("%s", not "%s"). Nothing from it is reused.'
                      % (_man_label or '?', _here_label or '?'))
        elif not _man_fp:
            # a manifest from before corpora were recorded: the folder is per-corpus by convention,
            # so trust it and SAY that the check could not be made
            _corpus_ok = True
            print('>>> Corpus Profiler: the existing profile records no corpus (written by an '
                  'earlier version); reusing it on the strength of the output folder.')
    _reused = 0

    for aid in selected:
        entry = REGISTRY.get(aid)
        if entry is None:
            continue
        rec = dict(id=aid, category=entry['category'], label=entry['label'],
                   kind=entry['kind'], files=[], error='', gui_script=entry.get('gui_script', ''))
        if entry['kind'] == 'batch':
            _done += 1
            _have = reusable_from_manifest(ctx, aid, _previous, _corpus_ok)
            if _have:
                rec['files'] = _have
                rec['reused'] = True
                # carry the previous run's code stamp across, so the round trip preserves WHICH
                # code produced these files rather than re-dating them to now
                for _p in (_previous or []):
                    if isinstance(_p, dict) and _p.get('id') == aid:
                        if _p.get('code'):
                            rec['code'] = _p['code']
                        break
                _reused += 1
                print('\nReusing %s (%d of %d) -- %d file(s) from a previous run, not re-run.'
                      % (entry['label'], _done, _n, len(_have)))
                results.append(rec)
                save_manifest(_outputDir, results, ctx)
                continue
            _t0 = _time.time()
            print('\nStarted running %s (%d of %d) at %s'
                  % (entry['label'], _done, _n, _time.strftime('%H:%M:%S')))
            try:
                rec['files'] = entry['run'](ctx) or []
                _dur = IO_user_interface_util.convert_time(_time.time() - _t0)[3]
                print('Finished running %s (%d of %d)%s.'
                      % (entry['label'], _done, _n, (' taking ' + _dur) if _dur else ''))
            except Exception as e:
                # no silent failure: record the error; the report shows it; the profile continues
                rec['error'] = str(e)
                print('Corpus Profiler: analysis "%s" FAILED: %s' % (aid, e))
        # kind == 'gui': nothing to run -- the report surfaces it as an "open the tool" pointer
        results.append(rec)
        # after EVERY analysis: whatever kills the next one, this one is not lost
        save_manifest(_outputDir, results, ctx)

    if _reused:
        print('\n>>> Corpus Profiler: %d of %d analyses were reused from a previous run of this '
              'corpus; %d were run.' % (_reused, _n, _n - _reused))
    save_manifest(_outputDir, results, ctx)
    return results


# ---------------------------------------------------------------------------------------------
# The manifest: what a run produced, written beside its outputs.
#
# The report and the summary are DERIVED from `results` -- which analysis produced which files. Until
# now that list existed only inside the running process, so improving a chart, an interpretation or the
# wording of the summary meant re-running the analyses to see it: hours, to redraw a page. The manifest
# is that list on disk, so the reports can be rebuilt from outputs that are already there.
# ---------------------------------------------------------------------------------------------
MANIFEST_NAME = 'NLP_corpus_profile_manifest.json'


def _manifest_store_path(path, outputDir):
    """A file's path as the manifest should record it: RELATIVE to the output folder when it lives
    inside it, absolute when it does not.

    Absolute paths made a profile folder unportable. Copy the folder - the obvious way to keep a
    baseline before re-running - and the copy's manifest still names files in the original: reuse
    reads the original's outputs, the copy gains nothing, and deleting the original breaks the copy
    entirely. Relative paths make a copied or moved profile work as itself.
    """
    try:
        rel = os.path.relpath(str(path), str(outputDir))
    except (ValueError, TypeError):          # different drive on Windows, or not a path at all
        return str(path)
    if rel.startswith('..'):                 # genuinely outside the folder: keep it absolute
        return str(path)
    return rel.replace(os.sep, '/')          # '/' so a manifest written on Windows reads on a Mac


def _manifest_resolve_path(path, outputDir):
    """The stored form back to a usable path: relative entries resolve against THIS output folder."""
    p = str(path).replace('/', os.sep)
    if os.path.isabs(p):
        return p
    return os.path.normpath(os.path.join(str(outputDir), p))


def save_manifest(outputDir, results, c=None):
    """Write what this run has produced SO FAR. Best-effort: a profile is not worth failing over it.

    Called after EVERY analysis, not once at the end. Written once at the end, a run that dies in
    its last minutes leaves no record of the thirty hours before it - which is exactly what happened
    on 30 July: the disk filled during the final charts, the manifest was never written, and a
    profile with every expensive table complete on disk could neither be rebuilt nor reused. A
    manifest is a few kilobytes; writing it 23 times costs nothing and makes every completed
    analysis survive whatever happens to the next one.

    Records the corpus, so a later run can tell whether these results describe the corpus in front
    of it - see reusable_from_manifest.
    """
    if not outputDir or not os.path.isdir(outputDir):
        return ''
    import json
    import time
    path = os.path.join(outputDir, MANIFEST_NAME)
    corpus_fp, corpus_label = corpus_fingerprint(c) if c is not None else ('', '')
    tmp = path + '.tmp'
    try:
        def _stamped(r):
            """Store the files relative, and stamp WHICH CODE produced them.

            A reused record keeps the stamp it already had - re-fingerprinting it here would write
            today's code against yesterday's files and defeat the check on the next run. Only an
            analysis that actually ran gets a fresh stamp.
            """
            out = dict(r, files=[_manifest_store_path(f, outputDir)
                                 for f in (r.get('files') or [])])
            if r.get('reused'):
                # keep whatever stamp came with it - INCLUDING none. Stamping reused files with
                # today's code would declare that today's code produced them, and the next run
                # would find them in order however much the analysis had changed since.
                return out
            code = analysis_code_fingerprint(r.get('id'))
            if code:
                out['code'] = code
            return out

        record = {'version': 3, 'written': time.strftime('%Y-%m-%d %H:%M:%S'),
                  'results': [_stamped(r) if isinstance(r, dict) else r for r in results]}
        if corpus_fp:
            record['corpus'] = corpus_fp
            record['corpus_label'] = corpus_label
        # written whole and moved into place: a manifest truncated by a full disk would be worse
        # than none, because the next run would read a half-list as the complete story
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump(record, fh, indent=1, default=str)
        os.replace(tmp, path)
        return path
    except Exception as e:
        print('Corpus Profiler: could not write the manifest (%s)' % e)
        try:
            os.remove(tmp)
        except OSError:
            pass
        return ''


def manifest_corpus(outputDir):
    """The corpus fingerprint recorded in the manifest, or '' (an older manifest has none)."""
    if not outputDir:
        return '', ''
    import json
    path = os.path.join(outputDir, MANIFEST_NAME)
    if not os.path.isfile(path):
        return '', ''
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception:
        return '', ''
    return str(data.get('corpus', '')), str(data.get('corpus_label', ''))


def analysis_code_fingerprint(aid, entry=None):
    """A hash of the code that produces analysis *aid*'s output. '' if it cannot be worked out.

    Reuse checked that the recorded files still existed, matched the corpus and carried no error. It
    never asked whether the code that WROTE them had changed since - so improving an analysis left
    every existing profile reusing the old output for ever. Symbolic space is what exposed it: the
    runner grew transitions, a heat map and an interactive timeline, and a profile that already had
    a manifest entry kept replaying the one-file record from the BUILD-only version. The new charts
    sat on disk, unlisted, and the summary looked as though the analysis had produced a lone csv.

    Worked out automatically rather than from a hand-kept table, so an analysis added tomorrow is
    covered with no extra code: the runner's own source, plus the source of every module in src/
    that the runner names, plus the modules THOSE name. Two levels reaches the real workers -
    _run_spatial_symbolic names GIS_symbolic_util, which names GIS_symbolic_typology_util, which is
    where the classification a reader would actually notice a change in lives.

    What it cannot see, deliberately: downloaded models, external lexicons, and a helper reached
    more than two levels down. Those are the same blind spots the parse-table sidecars have.
    """
    import hashlib
    import inspect
    import re

    entry = entry if entry is not None else REGISTRY.get(aid) or {}
    fn = entry.get('run')
    if not callable(fn):
        return ''                     # a GUI pointer produces no files; nothing to invalidate

    src_dir = os.path.dirname(os.path.abspath(__file__))

    def _source_of(path):
        try:
            with open(path, 'rb') as fh:
                return fh.read()
        except OSError:
            return b''

    def _modules_named_in(text):
        found = set()
        for name in set(re.findall(r'\b([A-Za-z_][A-Za-z0-9_]{2,})\b', text)):
            if os.path.isfile(os.path.join(src_dir, name + '.py')):
                found.add(name)
        return found

    try:
        body = inspect.getsource(fn)
    except Exception:
        return ''

    first = _modules_named_in(body)
    second = set()
    for name in sorted(first):
        second |= _modules_named_in(
            _source_of(os.path.join(src_dir, name + '.py')).decode('utf-8', 'replace'))
    modules = sorted(first | second)

    digest = hashlib.sha256()
    digest.update(body.encode('utf-8', 'replace'))
    for name in modules:
        digest.update(name.encode('utf-8'))
        digest.update(_source_of(os.path.join(src_dir, name + '.py')))
    return digest.hexdigest()[:16]


def reusable_from_manifest(c, aid, previous, corpus_ok):
    """The files a previous run produced for analysis *aid*, if they can be trusted. [] if not.

    THE POINT: reuse for EVERY analysis, from one rule, rather than a hand-written probe per
    analysis. Eight analyses had probes - the parses, where the hours were - and the other fifteen
    re-ran from scratch every time. That was defended as "the rest are cheap", which is true of any
    one of them and false of all of them together: a re-run after a crash spent an afternoon
    recomputing work that was already sitting on disk, and each new probe was another chance to
    match the wrong table.

    A probe guesses which file on disk belongs to an analysis, by name and columns. The manifest
    does not have to guess: the run that produced the file wrote down which analysis produced it.
    So this needs no per-analysis knowledge and cannot mismatch, and it covers an analysis added
    tomorrow with no extra code.

    Trusted means all of:
      - the previous run recorded this analysis with no error
      - every file it named is still on disk and NOT EMPTY (a full disk leaves 0-byte files, and
        one of those reused as real output is worse than re-running)
      - the manifest says it was built from THIS corpus (corpus_ok, computed once by the caller)
      - the code that produced them has not changed since (see analysis_code_fingerprint). An
        analysis that has been improved must RE-RUN, or the improvement never reaches a profile
        that already exists - which is every profile a returning user has.

    A manifest written before fingerprints were recorded has none. Those reuse, with a line saying
    the check could not be made, rather than forcing everyone's existing profile to recompute
    everything once; from this run on, each entry carries one.
    """
    if not previous or not corpus_ok:
        return []
    for rec in previous:
        if not isinstance(rec, dict) or rec.get('id') != aid:
            continue
        if rec.get('error'):
            return []                       # it failed last time; running it is the whole point
        stamped = str(rec.get('code') or '')
        current = analysis_code_fingerprint(aid)
        if stamped and current and stamped != current:
            print('>>> %s: the code that produces this changed since the last run (%s -> %s); '
                  're-running rather than reusing.' % (aid, stamped[:8], current[:8]))
            return []
        if current and not stamped:
            print('>>> %s: reusing, but this profile predates the code stamp, so "has the analysis '
                  'changed?" could not be checked.' % aid)
        files = [str(f) for f in rec.get('files') or []]
        if not files:
            return []
        for f in files:
            try:
                if not os.path.isfile(f) or os.path.getsize(f) == 0:
                    return []
            except OSError:
                return []
        return files
    return []


def load_manifest(outputDir):
    """The results list from a previous run, with vanished files dropped. [] if there is none.

    Files are re-checked rather than trusted: an output folder is a folder, and things get moved,
    renamed and deleted between a run and a rebuild.
    """
    if not outputDir:
        return []
    import json
    path = os.path.join(outputDir, MANIFEST_NAME)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception as e:
        print('Corpus Profiler: could not read the manifest (%s)' % e)
        return []

    results, missing = [], 0
    for rec in data.get('results', []):
        if not isinstance(rec, dict):
            continue
        # entries are stored relative to the output folder (older manifests hold absolute paths);
        # resolve against THIS folder so a copied or moved profile refers to its own files
        named = [_manifest_resolve_path(f, outputDir) for f in rec.get('files', [])]
        kept = [f for f in named if os.path.isfile(f)]
        missing += len(named) - len(kept)
        rec['files'] = kept
        results.append(rec)
    if missing:
        print('>>> Corpus Profiler: %d file(s) named in the manifest are no longer on disk '
              'and were left out of the rebuild' % missing)
    return results


# ---------------------------------------------------------------------------------------------
# Corpus header stats -- cheap counts for the report header. Reads the raw txt corpus directly
# so it works even if no analysis produced a statistics file.
# ---------------------------------------------------------------------------------------------
def parsed_sentence_count(outputDir, n_docs=0, parser_tag=''):
    """The corpus's sentence count as the PARSER counted it, or 0 if none is on disk.

    The parser's per-token tables (CoNLL / NER / POS) carry Document ID + Sentence ID with sentence IDs
    restarting in each document, so the corpus total is the sum of each document's highest ID. That is the
    number every downstream analysis works with, and so the one the report should show: the parser-free
    estimate below counts runs of . ! ? and reads every 'Mr.' and every abbreviation as a sentence end --
    on the Harry Potter corpus it says ~87,560 where Stanza says 69,591, a quarter too many.

    ONLY a per-token table is trusted, and only one whose Document ID really identifies documents. The
    relations table also has both column names, but its 'Document ID' holds 71,093 distinct values for 199
    documents -- summing maxima over that gave 16 million sentences, which is the kind of number that gets
    into a paper.

    *parser_tag* is the CONFIGURED parser ('stanza', 'corenlp', 'spacy'). A profile can hold tables from
    more than one of them and they do not agree: on Harry Potter, CoreNLP finds 79,389 sentences where
    Stanza finds 69,591, because they split sentences differently. There is no neutral answer -- the
    corpus has as many sentences as your parser says it has -- so the report quotes the parser named in
    its own header.
    """
    if not outputDir or not os.path.isdir(outputDir):
        return 0
    import glob
    import pandas as pd
    tag = (parser_tag or '').strip().lower()
    best = 0
    for p in sorted(glob.glob(os.path.join(outputDir, '**', '*.csv'), recursive=True)):
        b = os.path.basename(p).lower()
        if 'binned' in b or 'chart' in b or 'frequency' in b:
            continue
        if tag and tag not in b:
            continue
        try:
            head = pd.read_csv(p, nrows=1, encoding='utf-8', on_bad_lines='skip')
            columns = set(head.columns)
            # a real parse: one token per row
            if not {'Document ID', 'Sentence ID'}.issubset(columns):
                continue
            if not ({'Form', 'Word'} & columns):
                continue
            df = pd.read_csv(p, usecols=['Document ID', 'Sentence ID'],
                             encoding='utf-8', on_bad_lines='skip')
            if n_docs and df['Document ID'].nunique() != n_docs:
                continue
            total = int(pd.to_numeric(df['Sentence ID'], errors='coerce')
                        .groupby(df['Document ID']).max().sum())
        except Exception:
            continue
        best = max(best, total)
    return best


def corpus_header_stats(inputFilename, inputDir, outputDir='', parser_tag=''):
    import glob, re
    paths = []
    if inputDir:
        paths = sorted(glob.glob(os.path.join(inputDir, '*.txt')))
    elif inputFilename:
        paths = [inputFilename]
    n_docs = len(paths)
    n_words = 0
    n_chars = 0
    n_sents = 0
    for p in paths:
        try:
            with open(p, encoding='utf-8', errors='ignore') as fh:
                text = fh.read()
            n_words += len(text.split())
            n_chars += len(text)
            # rough sentence count: runs of end-of-sentence punctuation. Cheap and parser-free, and used
            # only when the run produced no parsed table to count from (see parsed_sentence_count).
            n_sents += len(re.findall(r'[.!?]+', text))
        except Exception:
            pass
    # prefer the parser's own count when this run produced one, so the header, the abstract and every
    # analysis downstream are all quoting the same number
    parsed = parsed_sentence_count(outputDir, n_docs, parser_tag)
    return dict(documents=n_docs, words=n_words, characters=n_chars,
                sentences=parsed or n_sents, sentences_estimated=not parsed)


# ---------------------------------------------------------------------------------------------
# build_report: write NLP_corpus_profile.html from the run results.  Pure/testable -- no imports
# of the analysis modules, no Tk.  Returns the report path.
# ---------------------------------------------------------------------------------------------
def _rel(href_path, report_dir):
    try:
        return os.path.relpath(href_path, report_dir).replace(os.sep, '/')
    except Exception:
        return href_path.replace(os.sep, '/')

def _esc(s):
    return _html.escape(str(s))

def build_report(outputDir, corpus_name, results, header_stats, run_config):
    report_path = os.path.join(outputDir, 'NLP_corpus_profile.html')
    report_dir = os.path.dirname(report_path)

    # group results by category, preserving CATEGORY_ORDER
    by_cat = {}
    for r in results:
        by_cat.setdefault(r['category'], []).append(r)

    total_files = sum(len(r['files']) for r in results)

    parts = []
    parts.append("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Corpus Profile — %s</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: 'Segoe UI', system-ui, Arial, sans-serif; margin: 0; line-height: 1.5;
         color: #1b1b1b; background: #fafafa; }
  @media (prefers-color-scheme: dark){ body{ color:#e8e8e8; background:#171717; } a{ color:#7db3ff; } }
  header { padding: 22px 28px; background: #2E5A88; color: #fff; }
  header h1 { margin: 0 0 4px; font-size: 22px; }
  header .sub { opacity: .9; font-size: 13px; }
  .stats { display: flex; flex-wrap: wrap; gap: 22px; padding: 16px 28px; background: #eef2f7;
           border-bottom: 1px solid #dde3ea; }
  @media (prefers-color-scheme: dark){ .stats{ background:#1f242b; border-color:#2b3540; } }
  .stat b { display: block; font-size: 22px; }
  .stat span { font-size: 12px; opacity: .7; }
  nav { padding: 10px 28px; position: sticky; top: 0; background: #fafafaee; backdrop-filter: blur(4px);
        border-bottom: 1px solid #e2e2e2; font-size: 13px; }
  @media (prefers-color-scheme: dark){ nav{ background:#171717ee; border-color:#2a2a2a; } }
  nav a { margin-right: 14px; text-decoration: none; }
  main { padding: 8px 28px 40px; max-width: 1100px; }
  details { border: 1px solid #e0e0e0; border-radius: 8px; margin: 14px 0; background: #fff; }
  @media (prefers-color-scheme: dark){ details{ background:#1e1e1e; border-color:#333; } }
  summary { cursor: pointer; padding: 12px 16px; font-weight: 600; font-size: 15px; }
  .cat-body { padding: 4px 16px 16px; }
  table { border-collapse: collapse; width: 100%%; font-size: 13px; }
  td, th { text-align: left; padding: 5px 8px; border-bottom: 1px solid #eee; }
  @media (prefers-color-scheme: dark){ td,th{ border-color:#2a2a2a; } }
  .analysis { font-weight: 600; padding-top: 10px; }
  .err { color: #b00020; font-size: 12px; }
  @media (prefers-color-scheme: dark){ .err{ color:#ff6b6b; } }
  .empty { opacity: .55; font-size: 12px; }
  footer { padding: 18px 28px; font-size: 12px; opacity: .7; }
</style></head><body>
""" % _esc(corpus_name))

    parts.append('<header><h1>Corpus Profile — %s</h1>'
                 '<div class="sub">%s</div>'
                 '<div class="sub" style="margin-top:8px">📄 Prefer the narrative? Read the '
                 '<a href="NLP_corpus_profile_summary.html" style="color:#cfe0f5;font-weight:600">'
                 'paper-style summary</a>.</div></header>'
                 % (_esc(corpus_name), _esc(run_config.get('subtitle', ''))))

    # header stat tiles, largest unit to smallest. Sentences were missing: the unit half the analyses
    # work in (sentiment, arcs, SVO, the CoNLL table) and the one a reader checks a chart's x axis against.
    sent_label = 'sentences (estimated)' if header_stats.get('sentences_estimated') else 'sentences'
    tiles = [('documents', 'documents'), ('sentences', sent_label),
             ('words', 'words'), ('characters', 'characters')]
    parts.append('<div class="stats">')
    for key, lab in tiles:
        parts.append('<div class="stat"><b>%s</b><span>%s</span></div>'
                     % (_esc('{:,}'.format(header_stats.get(key, 0))), _esc(lab)))
    parts.append('<div class="stat"><b>%s</b><span>output files</span></div>' % _esc('{:,}'.format(total_files)))
    parts.append('</div>')

    # nav
    parts.append('<nav>')
    for cat in CATEGORY_ORDER:
        if cat in by_cat:
            parts.append('<a href="#%s">%s</a>' % (cat, _esc(CATEGORY_TITLE[cat].split('  ')[0])))
    parts.append('</nav><main>')

    # per-category sections
    for cat in CATEGORY_ORDER:
        recs = by_cat.get(cat)
        if not recs:
            continue
        n = sum(len(r['files']) for r in recs)
        parts.append('<details id="%s" open><summary>%s &nbsp;<span class="empty">(%d files)</span></summary>'
                     '<div class="cat-body"><table>' % (cat, _esc(CATEGORY_TITLE[cat]), n))
        for r in recs:
            parts.append('<tr><td class="analysis" colspan="2">%s%s</td></tr>'
                         % (_esc(r['label']),
                            (' <span class="err">— failed: %s</span>' % _esc(r['error'])) if r['error'] else ''))
            if r.get('kind') == 'gui':
                parts.append('<tr><td style="width:60px"></td>'
                             '<td class="empty">→ has its own options — open the <b>%s</b> tool from the NLP Suite menu.</td></tr>'
                             % _esc(r.get('gui_script', '').replace('_main.py', '').replace('_', ' ')))
            elif r['files']:
                for f in r['files']:
                    parts.append('<tr><td style="width:60px"></td>'
                                 '<td><a href="%s">%s</a></td></tr>'
                                 % (_esc(_rel(f, report_dir)), _esc(os.path.basename(f))))
            elif not r['error']:
                parts.append('<tr><td></td><td class="empty">(no output files)</td></tr>')
        parts.append('</table></div></details>')

    parts.append('</main><footer>%s</footer></body></html>'
                 % _esc(run_config.get('footer', '')))

    with open(report_path, 'w', encoding='utf-8') as fh:
        fh.write(''.join(parts))
    return report_path


# ---------------------------------------------------------------------------------------------
# build_paper_summary: write NLP_corpus_profile_summary.html -- a readable, paper-style narrative
# of the same run. Where build_report is a navigable INDEX of every output file, this is the
# HEADLINE: numbered sections per dimension, the key charts embedded inline as figures, templated
# prose grounded in the actual counts, and every figure linked back to its source data.
#
# It is deliberately the AUTOMATABLE CORE of a hand-written paper: the facts, the charts and the
# shape are real and generated; the interpretive eloquence of a human author is not attempted.
# Pure/testable -- reads only the results list + header_stats, never re-runs an analysis.
# ---------------------------------------------------------------------------------------------
_IMG_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.svg')
_DATA_EXT = ('.csv', '.xlsx', '.xls', '.tsv')
_INTERACTIVE_EXT = ('.html', '.htm', '.kml')

# a natural lead-in per category so the templated prose reads as sentences, not labels
_CATEGORY_LEAD = {
    'counts':     'How big and how varied is the corpus? The profiler measured its size and spread, and looked '
                  'at vocabulary richness, frequency, word shape and document similarity.',
    'syntax':     'How is the language built? Every word was POS-tagged, so the corpus can be read as a '
                  'distribution of parts of speech — nouns, verbs, adjectives, adverbs, pronouns.',
    'semantics':  'What do the words mean? Nouns and verbs were aggregated up to three knowledge bases — '
                  'WordNet classes, VerbNet verb classes and FrameNet frames — and the most frequent words '
                  'were embedded with BERT into a 2-D t-SNE semantic map.',
    'topics':     'What is the corpus about? Topics were surveyed.',
    'entities':   'Who said what, and when? Gender, speaker-attributed dialogue/quotes and normalized dates '
                  'were extracted (Stanford CoreNLP). People, organizations and locations appear under Counts.',
    'spatial':    'Where does it all happen? Both geocodable and symbolic (narrative) space were considered.',
    'narrative':  'Who did what to whom? Subject-Verb-Object triples and semantic roles were derived.',
    'sentiment':  'How does the corpus feel? Sentiment was scored with a neural model.',
    'characters': 'Zooming in on the people of the corpus: how each character FEELS over the story '
                  '(NRC’s eight emotions, traced per character) and where each character MOVES '
                  'over the story (the places they pass through, animated along narrative time).',
}


def _humanize_file(path):
    """A readable caption from an output filename: drop the extension and NLP/date noise."""
    base = os.path.splitext(os.path.basename(path))[0]
    base = base.replace('_', ' ').replace('  ', ' ').strip()
    return base[:1].upper() + base[1:] if base else os.path.basename(path)


def _classify_files(files):
    """Split a rec's output files into (images, data, interactive) by extension."""
    imgs, data, inter = [], [], []
    for f in files:
        ext = os.path.splitext(str(f))[1].lower()
        if ext in _IMG_EXT:
            imgs.append(f)
        elif ext in _DATA_EXT:
            data.append(f)
        elif ext in _INTERACTIVE_EXT:
            inter.append(f)
    return imgs, data, inter


# ---------------------------------------------------------------------------------------------
# Finding INTERPRETATION. Each _interp_<category> reads the analysis's own output CSV(s) and
# returns a list of plain-language sentences stating what the numbers SAY -- not just that a file
# exists. Everything is defensive: a missing/odd file yields no sentence, never an exception.
# Files are located by keyword within the category's output list, so this is corpus-agnostic
# (filenames embed the corpus name). Grounded in the real newspaperArticles profile output.
# ---------------------------------------------------------------------------------------------
_PRONOUNS = {'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them', 'their',
             'theirs', 'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours', 'you', 'your', 'yours',
             'this', 'that', 'these', 'those', 'who', 'whom', 'whose', 'himself', 'herself'}

# copulas / auxiliaries / modals -- dropped from the "most frequent ACTIONS" line so the verbs read as
# real actions (know, make, find...) rather than "is / are / has". Kept elsewhere.
_LIGHT_VERBS = frozenset({'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am', "'s", "'m", "'re",
                          'has', 'have', 'had', 'having', 'do', 'does', 'did', 'doing', "'ll", "'d",
                          'will', 'would', 'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'get'})


def _read_csv(path):
    """Version-tolerant CSV read -> DataFrame or None (never raises)."""
    import pandas as pd
    try:
        return pd.read_csv(path)
    except Exception:
        for kw in ({'engine': 'python', 'on_bad_lines': 'skip'},
                   {'engine': 'python', 'error_bad_lines': False}):
            try:
                return pd.read_csv(path, **kw)
            except Exception:
                continue
    return None


def _find(files, *must, exclude=()):
    """First file whose basename contains ALL `must` keywords and none of `exclude` (case-insensitive)."""
    for f in files:
        b = os.path.basename(str(f)).lower()
        if b.endswith('.csv') and all(m.lower() in b for m in must) and not any(x.lower() in b for x in exclude):
            return f
    return None


def _num(df, *name_subs):
    """First column whose (lowercased) name contains any of name_subs, coerced to a numeric Series."""
    import pandas as pd
    for c in df.columns:
        cl = str(c).lower()
        if any(s in cl for s in name_subs):
            return pd.to_numeric(df[c], errors='coerce').dropna()
    return None


def _thousands(n):
    return '{:,}'.format(int(n))


def _interp_counts(files):
    f = _find(files, 'corpus_stats', exclude=('ungroup', 'group'))
    if not f:
        return []
    df = _read_csv(f)
    if df is None:
        return []
    sent, words, syll = _num(df, 'number of sentences'), _num(df, 'number of words'), _num(df, 'number of syllables')
    if sent is None or words is None or not len(sent) or sent.sum() == 0:
        return []
    tot_s, tot_w = int(sent.sum()), int(words.sum())
    line = ('The corpus runs to %s words across %s sentences — about %.1f words per sentence.'
            % (_thousands(tot_w), _thousands(tot_s), tot_w / tot_s if tot_s else 0))
    if syll is not None and syll.sum() > 0 and tot_w:
        line += (' Its %s syllables average %.2f per word, a rough gauge of lexical heft.'
                 % (_thousands(syll.sum()), syll.sum() / tot_w))
    return [line]


def _interp_vocabulary(files):
    f = _find(files, 'yule')
    if not f:
        return []
    df = _read_csv(f)
    if df is None:
        return []
    k = _num(df, 'yule', 'k value')
    if k is None or not len(k):
        return []
    return [('Vocabulary richness (Yule’s K — lower means a more varied, less repetitive vocabulary) '
             'averages %.1f across the documents, ranging from %.1f (richest) to %.1f (most repetitive).'
             % (k.mean(), k.min(), k.max()))]


def _interp_tfidf_similarity(files):
    # the "Document Similarity (TF-IDF Cosine)" matrix produced by the TF-IDF analysis: how much each PAIR
    # of documents shares the same distinctive vocabulary. Read it and say what it means, plainly.
    f = _find(files, 'tf-idf', 'similarity') or _find(files, 'tfidf', 'similarity')
    if not f:
        return []
    df = _read_csv(f)
    if df is None or df.shape[1] < 2:
        return []
    import pandas as pd
    labels = df.iloc[:, 0].astype(str).tolist()
    mat = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    n = min(len(labels), mat.shape[1])
    vals, best = [], (None, None, -1.0)
    for i in range(n):
        for j in range(i + 1, n):   # off-diagonal, upper triangle only
            v = mat.iloc[i, j]
            if pd.notna(v):
                vals.append(float(v))
                if float(v) > best[2]:
                    best = (labels[i], labels[j], float(v))
    if not vals:
        return []
    line = ('Document similarity (TF-IDF cosine) gauges how much each PAIR of documents shares the same '
            'distinctive vocabulary: 1.0 = near-identical wording, 0 = no salient words in common. The average '
            'pairwise similarity across the corpus is %.2f' % (sum(vals) / len(vals)))
    if best[0] is not None:
        line += (', and the most alike documents are “%s” and “%s” (%.2f). In the heatmap, bright blocks are '
                 'clusters of documents that talk alike, while dark rows are outliers with a vocabulary of '
                 'their own.' % (best[0], best[1], best[2]))
    else:
        line += '.'
    return [line]


def _interp_ner(files):
    # People/organizations/locations (NER), extracted with the configured parser. Reported under COUNTS
    # (NER is a basic descriptive extraction now, decoupled from the CoreNLP-only enrichments).
    findings = []
    f = _find(files, 'ner_all_ner', exclude=('bydoc', 'chart', 'group', 'no_hyperlinks', 'stats'))
    if not f:
        # Stanza/spaCy NER output isn't named 'ner_all_ner'; fall back to any NER csv (the NER+Word
        # column check below gates it, so a wrongly-picked file simply yields no findings).
        f = _find(files, '_ner', exclude=('bydoc', 'chart', 'group', 'no_hyperlinks', 'stats',
                                          'gender', 'svo', 'lemma'))
    if not f:
        return findings
    df = _read_csv(f)
    if df is not None and 'NER' in df.columns and 'Word' in df.columns:
        tags = df['NER'].astype(str).value_counts()
        if tags.sum() > 0:
            top_tags = ', '.join('%s (%s)' % (t, _thousands(c)) for t, c in tags.head(5).items())
            findings.append('The parser tagged %s entity mentions, led by %s.'
                            % (_thousands(tags.sum()), top_tags))
            named = df[~df['Word'].astype(str).str.lower().isin(_PRONOUNS)]['Word'].astype(str).value_counts()
            if len(named):
                names = ', '.join('%s (%d)' % (w, int(c)) for w, c in named.head(6).items())
                findings.append('Setting pronouns aside, the most frequently named entities are %s.' % names)
    return findings


def _interp_entities(files):
    # The CoreNLP-only enrichments: gender (coref-based), dialogue/quotes and normalized dates. NER is
    # reported separately under Counts (see _interp_ner).
    import pandas as pd
    findings = []
    fg = _find(files, 'gender', 'bydoc_freq', exclude=('chart',))
    if fg:
        df = _read_csv(fg)
        if df is not None and 'Gender' in df.columns:
            freqcol = next((c for c in df.columns if 'frequency_word' in str(c).lower()), None)
            if freqcol:
                g = df.groupby(df['Gender'].astype(str).str.upper())[freqcol].apply(
                    lambda s: pd.to_numeric(s, errors='coerce').sum())
                male, female = int(g.get('MALE', 0)), int(g.get('FEMALE', 0))
                if male + female > 0:
                    findings.append('Gendered references skew %s: %s male vs %s female mentions (%.0f%% male).'
                                    % ('male' if male >= female else 'female', _thousands(male),
                                       _thousands(female), 100 * male / (male + female)))
    fd = _find(files, 'normalized-date', exclude=('bydoc', 'chart', 'no_hyperlinks', 'group'))
    if fd:
        df = _read_csv(fd)
        if df is not None and len(df):
            typ = ''
            tcol = next((c for c in df.columns if str(c).lower().strip() == 'date type'), None)
            if tcol:
                vc = df[tcol].astype(str).value_counts()
                typ = ' — mostly ' + ', '.join('%s %s' % (int(v), k.lower()) for k, v in vc.head(3).items())
            findings.append('%s time expressions were extracted and normalized%s.' % (_thousands(len(df)), typ))
    if not findings:
        # The row ran but produced nothing -> CoreNLP + Java aren't installed (these features are CoreNLP-
        # only, with no Stanza/spaCy equivalent). Tell the user WHAT to install; the profiler uses CoreNLP
        # automatically for these once it's present -- no need to change the configured NLP package.
        findings.append(_EMPH + 'Gender, dialogue/quotes and normalized dates were NOT extracted: these '
                        'require Stanford CoreNLP and Java, which are not installed on this machine. '
                        'Install both from  Setup ▸ Download / install external software  (Java, then '
                        'Stanford CoreNLP); the profiler will then extract them automatically on the next '
                        'run — no need to change the NLP package. (People, organizations and locations are '
                        'still extracted, under Counts, with your configured parser.)')
    return findings


def _interp_semantics(files):
    findings = []
    for label, sub in (('Nouns', 'noun'), ('Verbs', 'verb')):
        f = _find(files, 'wordnet_up_' + sub, 'frequency') or _find(files, sub, 'frequency', 'wordnet')
        if not f:
            continue
        df = _read_csv(f)
        if df is None:
            continue
        catcol = next((c for c in df.columns if 'category' in str(c).lower()), None)
        frqcol = next((c for c in df.columns if 'frequency' in str(c).lower()), None)
        if not catcol or not frqcol:
            continue
        import pandas as pd
        df = df.assign(_f=pd.to_numeric(df[frqcol], errors='coerce')).dropna(subset=['_f'])
        top = df.sort_values('_f', ascending=False).head(5)
        if len(top):
            items = ', '.join('%s (%d)' % (str(r[catcol]), int(r['_f'])) for _, r in top.iterrows())
            findings.append('%s cluster into WordNet classes led by %s.' % (label, items))

    # VerbNet verb classes and FrameNet frames -- the other two knowledge bases, same lemma lists.
    def _top_cats(fkey, n=5):
        f = _find(files, fkey, 'frequency')
        if not f:
            return None
        df = _read_csv(f)
        if df is None:
            return None
        catcol = next((c for c in df.columns if 'category' in str(c).lower()), None)
        frqcol = next((c for c in df.columns if 'frequency' in str(c).lower()), None)
        if not catcol or not frqcol:
            return None
        import pandas as pd
        df = df.assign(_f=pd.to_numeric(df[frqcol], errors='coerce')).dropna(subset=['_f'])
        df = df[df[catcol].astype(str).str.lower() != 'not found']   # drop the unclassified bucket
        top = df.sort_values('_f', ascending=False).head(n)
        if not len(top):
            return None
        return ', '.join('%s (%d)' % (str(r[catcol]), int(r['_f'])) for _, r in top.iterrows())

    vn = _top_cats('verbnet_up_verb')
    if vn:
        findings.append('The same verbs sort into VerbNet classes (Levin-style syntactic-semantic verb '
                        'classes) led by %s.' % vn)
    fn_v = _top_cats('framenet_up_verb')
    if fn_v:
        findings.append('By FrameNet, the verbs evoke semantic frames led by %s.' % fn_v)
    fn_n = _top_cats('framenet_up_noun')
    if fn_n:
        findings.append('Nouns evoke FrameNet frames led by %s.' % fn_n)

    if not findings:
        # No WordNet/VerbNet/FrameNet findings -> the KB aggregation produced nothing (e.g. the Stanza
        # POS pass found no nouns/verbs, or the NLTK WordNet/VerbNet/FrameNet corpora aren't downloaded).
        # This is English-only and uses Stanza POS -- NO CoreNLP is involved. The BERT map may still have run.
        findings.append('Noun & verb knowledge-base classes (WordNet / VerbNet / FrameNet) were not '
                        'computed for this corpus (no nouns/verbs were found, or the WordNet/VerbNet/'
                        'FrameNet data isn’t installed; note the aggregation is English-only).')

    # BERT word embeddings -> interactive t-SNE map (an HTML chart, linked below)
    if any(('word2vec_vector' in os.path.basename(str(f)).lower() or 'tsne' in os.path.basename(str(f)).lower())
           and str(f).lower().endswith(('.html', '.htm')) for f in files):
        findings.append('BERT (all-distilroberta-v1) embedded the corpus’s most frequent words and projected them '
                        'into an interactive 2-D t-SNE semantic map — words placed near each other are used in '
                        'similar contexts (open the interactive chart below).')
    if findings:
        # AGENCY callout (red/bold), the semantic twin of the passive-voice note in Syntax.
        findings.append(_EMPH + 'NOMINALIZATION — recasting an action as a thing (“they decided” → “the '
                        'decision”, “they migrated” → “the migration”) — hides who acted, the semantic twin '
                        'of the passive and another marker of the DENIAL OF AGENCY. Run nominalization '
                        'analysis in the Semantic Analysis GUI.')
    return findings


def _interp_narrative(files):
    import pandas as pd
    findings = []
    fs = _find(files, 'svo', exclude=('sunburst', 'treemap', 'sankey', 'network', 'form', 'chart', 'bydoc'))
    if fs:
        df = _read_csv(fs)
        if df is not None and len(df):
            findings.append('Subject–Verb–Object extraction produced %s triples — the backbone of '
                            '“who did what to whom.”' % _thousands(len(df)))

            def _top(sub, label, n=6, drop=frozenset()):
                col = next((c for c in df.columns if sub in str(c).lower()), None)
                if not col:
                    return None
                vals = df[col].astype(str).str.strip()
                low = vals.str.lower()
                vals = vals[(vals.str.len() > 0) & (low != 'nan') & (~low.isin(_PRONOUNS | drop))
                            & (~low.str.startswith('inferred'))]   # drop SVO placeholder tokens
                vc = vals.value_counts()
                if not len(vc):
                    return None
                return ('The most frequent %s are %s.'
                        % (label, ', '.join('%s (%d)' % (v, int(c)) for v, c in vc.head(n).items())))
            for _line in (_top('verb', 'actions (verbs)', drop=_LIGHT_VERBS),
                          _top('subject', 'actors (subjects)'),
                          _top('object', 'objects acted upon')):
                if _line:
                    findings.append(_line)
    fr = _find(files, 'role-freq', 'chart')
    if fr:
        df = _read_csv(fr)
        if df is not None and 'Role' in df.columns and 'Count' in df.columns:
            cnt = pd.to_numeric(df['Count'], errors='coerce')
            df = df.assign(_c=cnt).dropna(subset=['_c']).sort_values('_c', ascending=False)
            if len(df):
                items = ', '.join('%s (%s)' % (str(r['Role']), _thousands(r['_c'])) for _, r in df.head(5).iterrows())
                findings.append('Semantic-role labeling filled %s role slots, dominated by %s.'
                                % (_thousands(df['_c'].sum()), items))
    return findings


def _interp_sentiment(files):
    for cand in files:
        b = os.path.basename(str(cand)).lower()
        if not (b.endswith('.csv') and 'sentiment' in b) or 'no_hyperlinks' in b or 'chart' in b:
            continue
        df = _read_csv(cand)
        if df is None:
            continue
        labcol = next((c for c in df.columns if 'sentiment label' in str(c).lower()), None)
        if not labcol:
            continue
        vc = df[labcol].astype(str).str.lower().value_counts()
        tot = int(vc.sum())
        if tot == 0:
            continue
        pos, neg, neu = int(vc.get('positive', 0)), int(vc.get('negative', 0)), int(vc.get('neutral', 0))
        lean = 'positive' if pos >= max(neg, neu) else ('negative' if neg >= neu else 'neutral')
        return [('Across %s scored sentences the mood leans %s: %.0f%% positive, %.0f%% negative, %.0f%% neutral.'
                 % (_thousands(tot), lean, 100 * pos / tot, 100 * neg / tot, 100 * neu / tot))]
    return []


def _interp_topics(files):
    f = _find(files, 'topic_keywords') or _find(files, 'gensim', 'topic', exclude=('distribution', 'representative'))
    if not f:
        return []
    df = _read_csv(f)
    if df is None:
        return []
    kwcol = next((c for c in df.columns if 'keyword' in str(c).lower()), None)
    if not kwcol or not len(df):
        return []
    preview = []
    for _, r in df.head(4).iterrows():
        kws = [k.strip() for k in str(r[kwcol]).split(',') if k.strip()]
        if kws:
            preview.append('“' + ', '.join(kws[:5]) + '”')
    if not preview:
        return []
    return ['Gensim LDA distilled %d topics; the leading ones cluster around %s.' % (len(df), '; '.join(preview)),
            'Topic modeling needs many documents for authoritative results — on a small corpus these are indicative.',
            'The profiler runs Gensim LDA (pure Python, nothing to install); MALLET (Java-based, often gives '
            'sharper topics) and BERTopic, plus coherence tuning to choose the number of topics, are available '
            'in the dedicated Topic Modeling GUI.']


_EIGHT_EMOTIONS = ('Anger', 'Anticipation', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Trust')


def _arc_strength(df, characters, n_bins=20, min_per_bin=3):
    """Is there a SHAPE in these emotion arcs, or only noise? A computed answer.

    A summary that lists the prevailing emotions and stops implies the arcs mean
    something. Often they do not: on the Harry Potter corpus every arc sits
    between 0.05 and 0.10 with spikes on top, which is a finding -- and the one
    a reader is least likely to reach unaided, because a busy chart looks
    eventful.

    The corpus is cut into *n_bins* equal stretches; each character's average
    for each emotion is taken per bin, and the SWING (highest bin minus lowest)
    says how much that emotion moves across the narrative. Bins holding fewer
    than *min_per_bin* of that character's sentences are dropped: an average
    over one sentence swings between 0 and 1 and would manufacture a shape.

    The eight emotion shares sum to 1, so an emotion sitting at its share of the
    whole would be 0.125 and a swing of 0.05 is a real movement. Returns
    sentences, or [] when there is not enough to say anything.
    """
    import numpy as np
    import pandas as pd
    present = [c for c in df.columns if str(c).strip().capitalize() in _EIGHT_EMOTIONS]
    if not present or 'Sentence ID' not in df.columns:
        return []

    ordered = df.copy()
    if 'Document ID' in ordered.columns:
        # sentence IDs restart in every document; ordering by them alone interleaves the corpus
        lengths = ordered.groupby('Document ID')['Sentence ID'].max().sort_index()
        offsets = lengths.cumsum().shift(1).fillna(0).astype(int)
        ordered['_pos'] = ordered['Document ID'].map(offsets) + ordered['Sentence ID']
    else:
        ordered['_pos'] = ordered['Sentence ID']
    ordered = ordered.dropna(subset=['_pos'])
    if not len(ordered):
        return []

    edges = np.linspace(ordered['_pos'].min(), ordered['_pos'].max(), n_bins + 1)
    swings, thin = [], 0
    for character in characters:
        rows = ordered[ordered['Character'].astype(str) == character]
        if len(rows) < min_per_bin * 2:
            continue
        bins = pd.cut(rows['_pos'], bins=edges, include_lowest=True)
        counts = rows.groupby(bins, observed=False)['_pos'].count()
        for col in present:
            means = rows.groupby(bins, observed=False)[col].mean().where(counts >= min_per_bin)
            means = means.dropna()
            if len(means) < 3:
                thin += 1
                continue
            # recorded even when it is ZERO: a flat arc is the finding here, and a
            # "> best so far" test would silently drop it and report that nothing
            # could be assessed
            swings.append((float(means.max() - means.min()),
                           str(col).strip().capitalize(), character))

    if not swings:
        return ['The arcs could not be assessed for shape: no character appears often enough, '
                'spread widely enough through the corpus, to average reliably.']

    swings.sort(reverse=True)
    biggest, emotion, who = swings[0]
    median = float(np.median([s for s, _, _ in swings]))
    scale = ' (all eight emotions equal would be 0.125)'

    if biggest < 0.05:
        verdict = ('These arcs are close to FLAT: no emotion moves by more than %.2f for any of the '
                   'leading characters%s. Read as noise around a constant, not as a story shape.'
                   % (biggest, scale))
    elif biggest < 0.15:
        verdict = ('These arcs show MODEST movement: the largest swing is %.2f — %s, %s%s.'
                   % (biggest, emotion, who, scale))
    else:
        verdict = ('These arcs show PRONOUNCED movement: the largest swing is %.2f — %s, %s%s.'
                   % (biggest, emotion, who, scale))

    findings = [verdict]
    # the largest swing is one series out of many; the median says whether the corpus MOVES or
    # whether one character-emotion pair does while everything else sits still
    if biggest >= 0.05:
        if median < 0.05:
            findings.append('That is the exception rather than the rule: the typical '
                            'character-emotion series swings only %.2f across the corpus, so most '
                            'of these arcs are flat and a few move.' % median)
        else:
            findings.append('And it is not an isolated case: the typical character-emotion series '
                            'swings %.2f across the corpus.' % median)
    if thin:
        findings.append('Some series were too thinly populated to read: %d character-emotion '
                        'combination%s had fewer than three usable stretches of text and were left '
                        'out of that assessment.' % (thin, '' if thin == 1 else 's'))
    return findings


def _interp_arcs(files):
    import pandas as pd
    f = (_find(files, 'character_emotion_arcs', exclude=('chart', 'no_hyperlinks', 'bydoc'))
         or _find(files, 'character', 'arc', exclude=('chart', 'no_hyperlinks')))
    if not f:
        return []
    df = _read_csv(f)
    if df is None or 'Character' not in df.columns:
        return []
    named = df[df['Character'].astype(str) != '_NARRATOR/UNATTRIBUTED_']
    if not len(named):
        return []
    counts = named['Character'].astype(str).value_counts()
    findings = ['Emotion arcs were traced for %d named character%s across the story; the most-followed are %s.'
                % (len(counts), '' if len(counts) == 1 else 's',
                   ', '.join('%s (%d)' % (c, int(n)) for c, n in counts.head(5).items()))]
    present = [c for c in df.columns if str(c).strip().capitalize() in _EIGHT_EMOTIONS]
    if present:
        sums = {str(c).strip().capitalize(): pd.to_numeric(df[c], errors='coerce').sum() for c in present}
        ordered = sorted(sums.items(), key=lambda kv: kv[1], reverse=True)
        total = sum(v for _, v in ordered) or 1
        lead = ', '.join('%s (%.0f%%)' % (k, 100 * v / total) for k, v in ordered[:3] if v > 0)
        if lead:
            findings.append('Across all characters the prevailing emotions are %s.' % lead)
    # ...and whether any of that MOVES. Naming the prevailing emotions and stopping implies a shape
    # the numbers may not support, which is the reading a busy chart will not give you.
    findings.extend(_arc_strength(df, list(counts.head(5).index)))
    return findings


def _find_pos_df(files):
    """The Stanza 'All POS' table (a CSV with a POS column)."""
    for cand in files:
        b = os.path.basename(str(cand)).lower()
        if b.endswith('.csv') and 'pos' in b and not any(k in b for k in ('no_hyperlinks', 'chart', 'bydoc')):
            df = _read_csv(cand)
            if df is not None and 'POS' in df.columns:
                return df
    return None


_POS_NAMES = [('NOUN', 'nouns'), ('VERB', 'verbs'), ('ADJ', 'adjectives'),
              ('ADV', 'adverbs'), ('PRON', 'pronouns'), ('AUX', 'auxiliaries'),
              ('PROPN', 'proper nouns')]


def _interp_syntax(files):
    df = _find_pos_df(files)
    if df is None:
        return []
    vc = df['POS'].astype(str).str.upper().value_counts()
    total = int(vc.sum())
    if total == 0:
        return []
    g = lambda t: int(vc.get(t, 0))
    breakdown = ', '.join('%s %s (%.0f%%)' % (_thousands(g(t)), name, 100 * g(t) / total)
                          for t, name in _POS_NAMES if g(t) > 0)
    findings = ['Of %s POS-tagged tokens, the parts of speech break down as %s.' % (_thousands(total), breakdown)]
    nouns, verbs = g('NOUN') + g('PROPN'), g('VERB')
    if verbs:
        ratio = nouns / verbs
        style = ('a nominal, descriptive style (more naming than doing)' if ratio > 1.5
                 else ('a verbal, action-driven style (more doing than naming)' if ratio < 0.9
                       else 'a balanced mix of naming and action'))
        findings.append('The noun-to-verb ratio is %.2f, indicating %s.' % (ratio, style))
    # lexical density: content words (nouns, proper nouns, verbs, adjectives, adverbs) as a share of tokens
    content = g('NOUN') + g('PROPN') + g('VERB') + g('ADJ') + g('ADV')
    findings.append('Lexical density — content words (nouns, verbs, adjectives, adverbs) as a share of all '
                    'tokens — is %.0f%%; the remainder are function words (pronouns, auxiliaries, determiners, '
                    'prepositions) that carry grammar rather than content.' % (100 * content / total))
    # how heavily things are modified
    if nouns:
        extra = (' and %.2f adverbs per verb' % (g('ADV') / verbs)) if verbs else ''
        findings.append('Modification density is %.2f adjectives per noun%s.' % (g('ADJ') / nouns, extra))
    # auxiliaries: tense/aspect/mood, and (with passives) voice
    if g('AUX'):
        findings.append('Auxiliaries make up %s tokens (%.0f%%) — the be/have/do and modal verbs that mark '
                        'tense, aspect, mood and voice; a high share often signals passives, perfects and '
                        'hedged/modal writing.' % (_thousands(g('AUX')), 100 * g('AUX') / total))
    if findings:
        # AGENCY callout (red/bold): passive voice can't be read off POS counts — it needs the dependency
        # parse. Flag it prominently because, with nominalization, it is a marker of the denial of agency.
        findings.append(_EMPH + 'PASSIVE VOICE — “X was killed” with no killer named — backgrounds or erases '
                        'the actor, a classic marker of the DENIAL OF AGENCY. It is invisible in POS counts '
                        'alone; the dependency parse detects it. Run it in the CoNLL Table Analyzer GUI '
                        '(dependency · clause · complexity · readability).')
    return findings


def _interp_characters(files):
    findings = _interp_arcs(files)   # emotional arcs: characters tracked + prevailing emotions
    # movement in space: the character->location tracking table (Entity + Location columns)
    mv = None
    for f in files:
        if not str(f).lower().endswith('.csv'):
            continue
        df = _read_csv(f)
        if df is not None and 'Entity' in df.columns and 'Location' in df.columns:
            mv = df
            break
    if mv is not None and len(mv):
        locs = mv['Location'].astype(str).value_counts()
        distinct = mv.assign(_e=mv['Entity'].astype(str), _l=mv['Location'].astype(str)) \
                     .groupby('_e')['_l'].nunique().sort_values(ascending=False)
        findings.append('Characters move through %d distinct places; the most frequented are %s.'
                        % (locs.nunique(), ', '.join('%s (%d)' % (l, int(n)) for l, n in locs.head(5).items())))
        if len(distinct):
            findings.append('The most mobile character is %s, appearing across %d different places.'
                            % (distinct.index[0], int(distinct.iloc[0])))
    return findings


def _interp_spatial(files):
    # read the NER location-tracking CSV (a 'Location' column) -> most-mentioned places + how many mapped
    for cand in files:
        if not str(cand).lower().endswith('.csv'):
            continue
        df = _read_csv(cand)
        if df is None or 'Location' not in df.columns:
            continue
        locs = df['Location'].astype(str).str.strip()
        locs = locs[(locs.str.len() > 0) & (locs.str.lower() != 'nan')]
        if not len(locs):
            continue
        vc = locs.value_counts()
        top = ', '.join('%s (%d)' % (p, int(cnt)) for p, cnt in vc.head(6).items())
        mapped = min(len(vc), 40)
        return ['The corpus names %s distinct places; the most frequent are %s. The top %s were geocoded '
                'and drawn as a proportional-symbol map (bubble size = number of mentions). This is a quick '
                'snapshot — the GIS GUI offers geocoder choice, an API key for speed, Google Earth / folium '
                'output and manual review.' % (_thousands(len(vc)), top, _thousands(mapped))]
    return []


def _interp_counts_vocabulary(files):
    # Counts, Vocabulary and Entities (NER) are one merged dimension now. Report them together but, when
    # 2+ sub-groups have findings, label them with bold sub-headings so the reader can still tell them apart.
    groups = [('Counts & measures', _interp_counts(files)),
              ('Vocabulary', _interp_vocabulary(files) + _interp_tfidf_similarity(files)),
              ('Entities (people, organizations, locations)', _interp_ner(files))]
    groups = [(head, f) for head, f in groups if f]
    if len(groups) <= 1:
        return groups[0][1] if groups else []
    out = []
    for head, f in groups:
        out += [_SUBHEAD + head] + f
    return out


# A finding may be flagged for RED/BOLD emphasis by prefixing it with this sentinel; the render loop in
# build_paper_summary strips it and styles that paragraph. Reserved for high-salience editorial callouts
# — notably passive voice and nominalization as markers of the DENIAL OF AGENCY (open the deeper GUI).
_EMPH = '@@EMPH@@'

# A finding prefixed with this sentinel is rendered as a BOLD SUB-HEADING (not a finding paragraph) —
# used to label sub-groups inside a merged dimension (e.g. "Counts & measures" vs "Vocabulary").
_SUBHEAD = '@@SUB@@'


def _interpret(category, files):
    """Dispatch to the per-category interpreter; always returns a (possibly empty) list of sentences."""
    fn = {'counts': _interp_counts_vocabulary, 'entities': _interp_entities,
          'semantics': _interp_semantics, 'narrative': _interp_narrative, 'syntax': _interp_syntax,
          'sentiment': _interp_sentiment, 'characters': _interp_characters, 'topics': _interp_topics,
          'spatial': _interp_spatial}.get(category)
    if not fn:
        return []
    try:
        return [s for s in fn(files) if s]
    except Exception as e:
        print('Corpus Profiler: interpretation for "%s" skipped: %s' % (category, e))
        return []


# ---------------------------------------------------------------------------------------------
# NATIVE charts. The summary draws its OWN inline-SVG bar charts from the finding numbers, so every
# quantitative dimension shows a chart -- independent of whether the underlying tool emitted a PNG,
# an Excel chart (not embeddable) or a Plotly HTML. Self-contained, theme-aware (CSS vars), no files.
# ---------------------------------------------------------------------------------------------
def _fmt_num(v):
    v = float(v)
    return _thousands(v) if v == int(v) else ('%.1f' % v)


def _svg_bar(title, pairs, max_bars=8):
    """A horizontal bar chart as an inline SVG string (theme-aware via CSS vars). '' if no data."""
    pairs = [(str(l), float(v)) for l, v in pairs if v is not None and float(v) > 0][:max_bars]
    if not pairs:
        return ''
    mx = max(v for _, v in pairs) or 1.0
    row_h, top, label_w, W = 22, 24, 156, 560
    bar_area = W - label_w - 52
    H = top + row_h * len(pairs) + 6
    out = ['<figure class="chart"><svg viewBox="0 0 %d %d" class="svgchart" '
           'preserveAspectRatio="xMinYMin meet" role="img">' % (W, H),
           '<text x="0" y="15" class="svg-title">%s</text>' % _esc(title)]
    y = top
    for lab, val in pairs:
        bw = max(2.0, bar_area * val / mx)
        disp = (lab[:24] + '…') if len(lab) > 25 else lab
        out.append('<text x="%d" y="%d" class="svg-lab" text-anchor="end">%s</text>'
                   % (label_w - 6, y + 14, _esc(disp)))
        out.append('<rect x="%d" y="%d" width="%.1f" height="14" rx="3" class="svg-bar"/>'
                   % (label_w, y + 3, bw))
        out.append('<text x="%.1f" y="%d" class="svg-val">%s</text>'
                   % (label_w + bw + 5, y + 14, _esc(_fmt_num(val))))
        y += row_h
    out.append('</svg></figure>')
    return ''.join(out)


def _chart_specs(category, files):
    """Return [(title, [(label, value), ...]), ...] of bar charts to draw natively for this category."""
    import pandas as pd
    try:
        specs = []
        if category == 'entities':
            f = _find(files, 'ner_all_ner', exclude=('bydoc', 'chart', 'group', 'no_hyperlinks', 'stats'))
            if f:
                df = _read_csv(f)
                if df is not None and 'NER' in df.columns:
                    tags = df['NER'].astype(str).value_counts().head(8)
                    specs.append(('Entity types (mentions)', list(tags.items())))
                    if 'Word' in df.columns:
                        named = df[~df['Word'].astype(str).str.lower().isin(_PRONOUNS)]['Word'] \
                            .astype(str).value_counts().head(8)
                        if len(named):
                            specs.append(('Most-named entities', list(named.items())))
        elif category == 'semantics':
            for label, sub in (('Noun classes (WordNet)', 'noun'), ('Verb classes (WordNet)', 'verb')):
                f = _find(files, 'wordnet_up_' + sub, 'frequency') or _find(files, sub, 'frequency', 'wordnet')
                if not f:
                    continue
                df = _read_csv(f)
                if df is None:
                    continue
                cc = next((c for c in df.columns if 'category' in str(c).lower()), None)
                fc = next((c for c in df.columns if 'frequency' in str(c).lower()), None)
                if cc and fc:
                    d = df.assign(_f=pd.to_numeric(df[fc], errors='coerce')).dropna(subset=['_f']) \
                        .sort_values('_f', ascending=False).head(8)
                    specs.append((label, [(str(r[cc]), r['_f']) for _, r in d.iterrows()]))
        elif category == 'sentiment':
            for f in files:
                b = os.path.basename(str(f)).lower()
                if not (b.endswith('.csv') and 'sentiment' in b) or 'no_hyperlinks' in b or 'chart' in b:
                    continue
                df = _read_csv(f)
                lc = next((c for c in df.columns if 'sentiment label' in str(c).lower()), None) if df is not None else None
                if lc:
                    vc = df[lc].astype(str).str.lower().value_counts()
                    pairs = [(k.title(), float(vc.get(k, 0))) for k in ('positive', 'neutral', 'negative')]
                    if any(v for _, v in pairs):
                        specs.append(('Sentence sentiment', pairs))
                        break
        elif category == 'characters':
            f = (_find(files, 'character_emotion_arcs', exclude=('chart', 'no_hyperlinks', 'bydoc'))
                 or _find(files, 'character', 'arc', exclude=('chart',)))
            if f:
                df = _read_csv(f)
                if df is not None:
                    present = [c for c in df.columns if str(c).strip().capitalize() in _EIGHT_EMOTIONS]
                    sums = [(str(c).strip().capitalize(), float(pd.to_numeric(df[c], errors='coerce').sum()))
                            for c in present]
                    sums = sorted([p for p in sums if p[1] > 0], key=lambda x: x[1], reverse=True)
                    if sums:
                        specs.append(('Prevailing emotions (NRC)', sums))
        elif category == 'narrative':
            fr = _find(files, 'role-freq', 'chart')
            if fr:
                df = _read_csv(fr)
                if df is not None and 'Role' in df.columns and 'Count' in df.columns:
                    d = df.assign(_c=pd.to_numeric(df['Count'], errors='coerce')).dropna(subset=['_c']) \
                        .sort_values('_c', ascending=False).head(8)
                    specs.append(('Semantic roles (SRL)', [(str(r['Role']), r['_c']) for _, r in d.iterrows()]))
        elif category == 'syntax':
            df = _find_pos_df(files)
            if df is not None:
                vc = df['POS'].astype(str).str.upper().value_counts().head(10)
                specs.append(('Parts of speech', list(vc.items())))
        elif category == 'counts':
            f = _find(files, 'corpus_stats', exclude=('ungroup', 'group'))
            if f:
                df = _read_csv(f)
                if df is not None:
                    wc = next((c for c in df.columns if 'number of words' in str(c).lower()), None)
                    idc = next((c for c in df.columns if str(c).lower().strip() == 'document id'), None)
                    if wc:
                        labels = df[idc].astype(str) if idc else df.index.astype(str)
                        pairs = [('Doc ' + str(l), float(v)) for l, v
                                 in zip(labels, pd.to_numeric(df[wc], errors='coerce')) if v == v]
                        if pairs:
                            specs.append(('Words per document', pairs))
        elif category == 'vocabulary':
            f = _find(files, 'yule')
            if f:
                df = _read_csv(f)
                if df is not None:
                    kc = next((c for c in df.columns if 'yule' in str(c).lower() or 'k value' in str(c).lower()), None)
                    idc = next((c for c in df.columns if str(c).lower().strip() == 'document id'), None)
                    if kc:
                        labels = df[idc].astype(str) if idc else df.index.astype(str)
                        pairs = [('Doc ' + str(l), float(v)) for l, v
                                 in zip(labels, pd.to_numeric(df[kc], errors='coerce')) if v == v]
                        if pairs:
                            specs.append(("Vocabulary richness — Yule's K per document (lower = richer)", pairs))
        return specs
    except Exception as e:
        print('Corpus Profiler: chart specs for "%s" skipped: %s' % (category, e))
        return []


def _data_uri(path, max_bytes=2_200_000):
    """base64 data: URI for an image so it embeds INLINE in the summary and always renders (portable,
    survives moving/emailing the file). '' if missing or larger than max_bytes (avoids bloat)."""
    try:
        ext = os.path.splitext(str(path))[1].lower().lstrip('.')
        ext = 'jpeg' if ext == 'jpg' else ext
        if ext not in ('png', 'jpeg', 'gif', 'svg') or os.path.getsize(path) > max_bytes:
            return ''
        import base64
        with open(path, 'rb') as fh:
            b64 = base64.b64encode(fh.read()).decode('ascii')
        return 'data:%s;base64,%s' % ('image/svg+xml' if ext == 'svg' else 'image/' + ext, b64)
    except Exception:
        return ''


def _make_wordcloud(inputDir, inputFilename, outputDir):
    """Generate a corpus wordcloud PNG (the iconic 'at a glance' visual). Returns its path or ''."""
    try:
        import glob as _glob
        from wordcloud import WordCloud, STOPWORDS
        paths = (sorted(_glob.glob(os.path.join(inputDir, '*.txt'))) if inputDir
                 else ([inputFilename] if inputFilename else []))
        texts = []
        for p in paths[:300]:
            try:
                with open(p, encoding='utf-8', errors='ignore') as fh:
                    texts.append(fh.read())
            except Exception:
                pass
        text = ' '.join(texts).strip()
        if len(text) < 50:
            return ''
        wc = WordCloud(width=1000, height=460, background_color='white', collocations=False,
                       stopwords=set(STOPWORDS), max_words=150, prefer_horizontal=0.9).generate(text)
        # its own folder, like every other output. The summary EMBEDS the wordcloud as base64, so
        # this file on disk is a spare copy and nothing links to it - which is exactly why it should
        # not sit in the folder a reader opens.
        out = os.path.join(_analysis_dir({'outputDir': outputDir, 'inputDir': inputDir,
                                          'inputFilename': inputFilename}, 'wordcloud'),
                           'NLP_corpus_wordcloud.png')
        wc.to_file(out)
        return out
    except Exception as e:
        print('Corpus Profiler: wordcloud skipped: %s' % e)
        return ''


def build_paper_summary(outputDir, corpus_name, results, header_stats, run_config,
                        report_basename='NLP_corpus_profile.html'):
    summary_path = os.path.join(outputDir, 'NLP_corpus_profile_summary.html')
    report_dir = os.path.dirname(summary_path)

    by_cat = {}
    for r in results:
        by_cat.setdefault(r['category'], []).append(r)
    cats_present = [c for c in CATEGORY_ORDER if c in by_cat]

    n_docs = header_stats.get('documents', 0)
    n_words = header_stats.get('words', 0)
    n_chars = header_stats.get('characters', 0)
    n_sents = header_stats.get('sentences', 0)
    avg_words = int(round(n_words / n_docs)) if n_docs else 0
    avg_sents = int(round(n_sents / n_docs)) if n_docs else 0
    total_files = sum(len(r['files']) for r in results)
    ran = [r for r in results if r.get('kind') == 'batch' and not r.get('error')]
    failed = [r for r in results if r.get('error')]

    def _fmt(n):
        return '{:,}'.format(n)

    # ---- abstract (templated from the real counts) ----
    dims = ', '.join(CATEGORY_TITLE[c].split('  ')[0].rstrip('?').strip().lower() for c in cats_present)
    # the TOTAL number of sentences, not only the per-document average: it is the unit half the analyses
    # work in, and a reader checking a chart's x axis against the corpus had no figure to check it against
    sents_estimated = ' (estimated)' if header_stats.get('sentences_estimated') else ''
    abstract = (
        'This report profiles the corpus <b>%s</b>, comprising <b>%s</b> document%s totaling '
        '<b>%s</b> sentences%s and <b>%s</b> words (%s characters), an average of <b>%s</b> words and '
        '<b>%s</b> sentences per document. '
        'The Corpus Profiler ran <b>%d</b> automated analys%s across <b>%d</b> dimension%s — %s — '
        'producing <b>%s</b> output file%s. '
        '<span style="color:#c1121f;font-weight:700">The findings are summarized below; every figure '
        'links to the source data, and the full navigable index of all outputs is available in the '
        '<a href="%s" style="color:var(--accent);font-weight:700">companion report</a>.</span>'
        % (_esc(corpus_name), _fmt(n_docs), '' if n_docs == 1 else 's',
           _fmt(n_sents), sents_estimated,
           _fmt(n_words), _fmt(n_chars), _fmt(avg_words), _fmt(avg_sents),
           len(ran), 'is' if len(ran) == 1 else 'es',
           len(cats_present), '' if len(cats_present) == 1 else 's', _esc(dims),
           _fmt(total_files), '' if total_files == 1 else 's',
           _esc(report_basename)))

    parts = []
    parts.append("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Corpus Profile — a paper-style summary — %s</title>
<style>
  :root{
    --bg:#fbfaf8; --ink:#1c1b19; --muted:#6b6862; --rule:#e4e1da; --card:#ffffff;
    --accent:#2E5A88; --accent-soft:#eef2f7; color-scheme: light dark;
  }
  @media (prefers-color-scheme: dark){
    :root{ --bg:#16181c; --ink:#e9e6e0; --muted:#9a968e; --rule:#2a2d33; --card:#1d2025;
           --accent:#7db3ff; --accent-soft:#1f2a38; }
  }
  *{ box-sizing:border-box; }
  body{ margin:0; background:var(--bg); color:var(--ink);
        font-family:Georgia,'Iowan Old Style',Cambria,'Times New Roman',serif; line-height:1.62; }
  .wrap{ max-width:760px; margin:0 auto; padding:0 26px 72px; }
  .eyebrow{ font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; letter-spacing:.18em;
            text-transform:uppercase; color:var(--accent); font-weight:700; }
  header.paper{ padding:52px 0 22px; border-bottom:2px solid var(--accent); margin-bottom:4px; }
  header.paper h1{ font-size:34px; line-height:1.15; margin:12px 0 10px; text-wrap:balance; font-weight:700; }
  .byline{ font-family:'Segoe UI',system-ui,sans-serif; font-size:13px; color:var(--muted); }
  .abstract{ font-size:16.5px; margin:26px 0 6px; }
  .abstract .lead{ font-family:'Segoe UI',system-ui,sans-serif; font-size:11px; letter-spacing:.16em;
                   text-transform:uppercase; color:var(--muted); display:block; margin-bottom:6px; }
  .figures-strip{ display:flex; flex-wrap:wrap; gap:14px; margin:30px 0 8px; }
  .kpi{ flex:1 1 120px; background:var(--accent-soft); border-radius:10px; padding:14px 16px; }
  .kpi b{ font-family:'Segoe UI',system-ui,sans-serif; font-size:24px; display:block; }
  .kpi span{ font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; color:var(--muted); }
  section.dim{ padding-top:16px; }
  h2.dim{ font-size:23px; margin:34px 0 4px; text-wrap:balance; }
  h2.dim .num{ font-family:'Segoe UI',system-ui,sans-serif; color:var(--accent); font-weight:700;
               font-size:15px; margin-right:10px; vertical-align:2px; }
  .lead-p{ margin:8px 0 4px; }
  .finding{ margin:12px 0; font-size:16.5px; padding-left:15px; border-left:3px solid var(--accent); }
  figure{ margin:22px 0; }
  figure img{ display:block; width:100%%; height:auto; border:1px solid var(--rule); border-radius:8px;
              background:var(--card); }
  figure iframe.chartframe{ display:block; width:100%%; height:460px; border:1px solid var(--rule);
                            border-radius:8px; background:#ffffff; }
  figure.chart{ margin:18px 0; }
  svg.svgchart{ width:100%%; height:auto; max-width:560px; display:block; }
  .svg-title{ font:600 13px 'Segoe UI',system-ui,sans-serif; fill:currentColor; }
  .svg-lab{ font:12px 'Segoe UI',system-ui,sans-serif; fill:var(--muted); }
  .svg-val{ font:600 12px 'Segoe UI',system-ui,sans-serif; fill:var(--muted); }
  rect.svg-bar{ fill:var(--accent); opacity:.88; }
  figure.wordcloud{ margin:26px 0 8px; }
  figure.wordcloud img{ width:100%%; height:auto; border:1px solid var(--rule); border-radius:10px; }
  .interactive{ font-family:'Segoe UI',system-ui,sans-serif; font-size:13px; margin:14px 0;
                padding:9px 13px; background:var(--accent-soft); border-radius:8px; }
  .interactive a{ color:var(--accent); text-decoration:none; white-space:nowrap; }
  .interactive a:hover{ text-decoration:underline; }
  figcaption{ font-family:'Segoe UI',system-ui,sans-serif; font-size:12.5px; color:var(--muted);
              margin-top:8px; }
  figcaption .fnum{ color:var(--accent); font-weight:700; }
  .sources{ font-family:'Segoe UI',system-ui,sans-serif; font-size:12.5px; color:var(--muted);
            border-left:3px solid var(--rule); padding:2px 0 2px 14px; margin:14px 0; }
  .sources a{ color:var(--accent); text-decoration:none; }
  .sources a:hover{ text-decoration:underline; }
  .note{ font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; color:var(--muted); font-style:italic; }
  .err{ color:#b00020; } @media (prefers-color-scheme: dark){ .err{ color:#ff6b6b; } }
  a{ color:var(--accent); }
  footer.paper{ margin-top:48px; padding-top:18px; border-top:1px solid var(--rule);
                font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; color:var(--muted); }
  .toc{ font-family:'Segoe UI',system-ui,sans-serif; margin:26px 0 6px; padding:16px 20px;
        border:1px solid var(--rule); border-radius:8px; background:rgba(127,127,127,.05); }
  .toc .toc-h{ font-weight:700; font-size:12px; letter-spacing:.08em; text-transform:uppercase;
               color:var(--muted); margin:0 0 10px; }
  .toc ol{ margin:0; padding:0; list-style:none; columns:2; column-gap:34px; }
  .toc li{ margin:5px 0; font-size:14px; break-inside:avoid; }
  .toc a{ color:var(--accent); text-decoration:none; }
  .toc a:hover{ text-decoration:underline; }
  .toc .tnum{ display:inline-block; min-width:1.4em; color:var(--muted); font-weight:700; }
  @media (max-width:640px){ .toc ol{ columns:1; } }
  section.dim{ scroll-margin-top:20px; }
</style></head><body><div class="wrap">
""" % _esc(corpus_name))

    parts.append('<header class="paper"><div class="eyebrow">Corpus Profile · paper-style summary</div>'
                 '<h1>%s</h1><div class="byline">%s</div></header>'
                 % (_esc(corpus_name), _esc(run_config.get('subtitle', ''))))

    parts.append('<div class="abstract"><span class="lead">Abstract</span>%s</div>' % abstract)

    # ---- linked Table of Contents: at a glance, what the summary covers + jump to any dimension.
    #      The numbers match the section headings below (and the trailing statistics section). ----
    _toc = ['<nav class="toc"><div class="toc-h">Contents</div><ol>']
    for _i, _cat in enumerate(cats_present, 1):
        _toc.append('<li><span class="tnum">%d.</span><a href="#sec-%d">%s</a></li>'
                    % (_i, _i, _esc(CATEGORY_TITLE[_cat])))
    _toc.append('<li><span class="tnum">+</span><a href="#sec-stats">Going further — statistics on '
                'these results</a></li>')
    _toc.append('</ol></nav>')
    parts.append(''.join(_toc))

    # by-the-numbers strip
    kpis = [(_fmt(n_docs), 'documents'), (_fmt(n_words), 'words'),
            (_fmt(avg_words), 'avg words / document'), (_fmt(total_files), 'output files')]
    parts.append('<div class="figures-strip">')
    for val, lab in kpis:
        parts.append('<div class="kpi"><b>%s</b><span>%s</span></div>' % (_esc(val), _esc(lab)))
    parts.append('</div>')

    # corpus WORDCLOUD -- the iconic 'at a glance' visual, embedded INLINE as base64 so it always renders
    _wc = _make_wordcloud(run_config.get('inputDir', ''), run_config.get('inputFilename', ''), outputDir)
    _wc_uri = _data_uri(_wc, max_bytes=3_500_000) if _wc else ''
    if _wc_uri:
        parts.append('<figure class="wordcloud"><img src="%s" alt="corpus wordcloud" loading="lazy">'
                     '<figcaption>The corpus at a glance — its most frequent words.</figcaption></figure>'
                     % _wc_uri)

    # ---- numbered sections, one per dimension that produced results ----
    fig_no = 0
    sec_no = 0
    MAX_FIG_PER_SECTION = 4
    for cat in cats_present:
        recs = by_cat[cat]
        sec_no += 1
        parts.append('<section class="dim" id="sec-%d"><h2 class="dim"><span class="num">%d</span>%s</h2>'
                     % (sec_no, sec_no, _esc(CATEGORY_TITLE[cat])))
        parts.append('<p class="lead-p">%s</p>' % _esc(_CATEGORY_LEAD.get(cat, '')))

        # INTERPRETATION: read this dimension's output CSVs and state what they say, in prose
        cat_files = []
        for r in recs:
            cat_files += r.get('files', [])
        for _finding in _interpret(cat, cat_files):
            if _finding.startswith(_SUBHEAD):   # bold sub-heading labelling a sub-group of the dimension
                parts.append('<p style="font-weight:700;margin:16px 0 3px">%s</p>'
                             % _esc(_finding[len(_SUBHEAD):]))
            elif _finding.startswith(_EMPH):   # high-salience callout (e.g. agency markers) -> red + bold
                parts.append('<p class="finding" style="color:#c1121f;font-weight:700">%s</p>'
                             % _esc(_finding[len(_EMPH):]))
            else:
                parts.append('<p class="finding">%s</p>' % _esc(_finding))

        # NATIVE inline-SVG charts, drawn from the numbers -> a chart in every quantitative section,
        # regardless of whether the tool emitted a PNG, an Excel chart, or a Plotly HTML.
        for _ctitle, _cpairs in _chart_specs(cat, cat_files):
            _svg = _svg_bar(_ctitle, _cpairs)
            if _svg:
                parts.append(_svg)

        # gather this dimension's outputs
        all_imgs, all_data, all_inter, gui_ptrs, errs = [], [], [], [], []
        for r in recs:
            if r.get('error'):
                errs.append((r['label'], r['error']))
            if r.get('kind') == 'gui':
                gui_ptrs.append(r.get('gui_script', '').replace('_main.py', '').replace('_', ' ').strip())
                continue
            imgs, data, inter = _classify_files(r.get('files', []))
            all_imgs += imgs
            all_data += data
            all_inter += inter

        # embed PNG charts INLINE as base64 data-URIs -> they always render, even if the summary file
        # is moved or emailed (relative <img src> can silently break; that is why charts looked absent).
        _shown = 0
        for img in all_imgs:
            if _shown >= MAX_FIG_PER_SECTION:
                break
            uri = _data_uri(img)
            if not uri:
                continue
            _shown += 1
            fig_no += 1
            parts.append('<figure><img src="%s" alt="%s" loading="lazy">'
                         '<figcaption><span class="fnum">Figure %d.</span> %s</figcaption></figure>'
                         % (uri, _esc(_humanize_file(img)), fig_no, _esc(_humanize_file(img))))
        if len(all_imgs) > _shown:
            parts.append('<p class="note">+%d more chart%s for this dimension in the '
                         '<a href="%s">full report</a>.</p>'
                         % (len(all_imgs) - _shown, '' if len(all_imgs) - _shown == 1 else 's',
                            _esc(report_basename)))

        # interactive charts (Plotly sunburst/treemap/sankey, network graphs, migration maps) are big
        # (~3-4 MB) CDN-based HTML that browsers WON'T render embedded from a local file -> link them
        # prominently instead of showing a blank iframe.
        html_charts = [f for f in all_inter if str(f).lower().endswith(('.html', '.htm'))]
        if html_charts:
            # Only the LABEL is red (the emphasized pointer); the chart links themselves are the accent
            # BLUE so the reader recognizes them as hyperlinks, per convention.
            links = ' &nbsp;·&nbsp; '.join('<a href="%s" style="color:var(--accent);font-weight:700">▶&nbsp;%s</a>'
                                           % (_esc(_rel(h, report_dir)), _esc(_humanize_file(h)))
                                           for h in html_charts[:6])
            parts.append('<p class="interactive">'
                         '<span style="color:#c1121f;font-weight:700"><b>Interactive charts</b> '
                         '(open in browser to visualize):</span> %s</p>' % links)

        # source-data links (csv/xlsx) + remaining artifacts (kml, extra charts)
        _linked = set(html_charts[:6])
        srcs = all_data + [f for f in all_inter if f not in _linked]
        if srcs:
            links = ' · '.join('<a href="%s">%s</a>' % (_esc(_rel(s, report_dir)), _esc(os.path.basename(s)))
                               for s in srcs[:12])
            more = ('  (+%d more)' % (len(srcs) - 12)) if len(srcs) > 12 else ''
            parts.append('<div class="sources"><b>Source data:</b> %s%s</div>' % (links, _esc(more)))

        # GUI-only dimensions (geocoding, topics, deeper tools) -> honest pointer
        if gui_ptrs and not all_imgs and not srcs:
            parts.append('<p class="note" style="color:#c1121f;font-weight:700">This dimension is explored '
                         'interactively — open the <b>%s</b> tool from the NLP Suite menu.</p>'
                         % _esc(', '.join(gui_ptrs)))

        # failures surfaced, never swallowed
        for lab, err in errs:
            parts.append('<p class="note err">%s could not be completed: %s</p>'
                         % (_esc(lab), _esc(err)))

        parts.append('</section>')

    # ---- capability callout: the statistical hypothesis tests available on ANY csv the profiler emits.
    #      These are NOT run in the batch (they need the user to choose columns/groups), but the profiler
    #      produces exactly the data they consume -- so we advertise them, with a red/bold how-to-run. ----
    parts.append(
        '<section class="dim" id="sec-stats"><h2 class="dim"><span class="num">+</span>Going further — '
        'statistics on these results</h2>'
        '<p class="lead-p">Every table above is a csv you can test statistically. The suite\'s '
        '<b>Statistical Analyses of csv Files</b> tool runs, on any of these outputs:</p>'
        '<ul>'
        '<li><b>Mann-Whitney U / Kruskal-Wallis</b> — do two or more groups differ?</li>'
        '<li><b>Log-likelihood</b> — which words are over-represented vs. another corpus (keyness)?</li>'
        '<li><b>Chi-square (independence)</b> — is a cross-tabulated association significant?</li>'
        '<li><b>Correlation (Spearman / Kendall)</b> — do two measures move together?</li>'
        '<li><b>Mann-Kendall</b> — is there a monotonic trend over time?</li>'
        '<li><b>Change-point detection</b> — when does a temporal series shift?</li>'
        '<li><b>Permutation test</b> — a distribution-free difference between two groups</li>'
        '<li><b>Inter-annotator agreement</b> — Cohen\'s / Fleiss\' kappa</li>'
        '</ul>'
        '<p class="finding" style="color:#c1121f;font-weight:700">To run any of these, open the '
        '<b>Statistical Analyses of csv Files</b> GUI from the NLP Suite menu and choose one of this '
        'profile\'s csv outputs as input — the profiler produces the data; the Statistics GUI tests it.</p>'
        '</section>')

    # ---- methods / data footer ----
    if failed:
        parts.append('<p class="note err">%d analys%s did not complete; see the notes above.</p>'
                     % (len(failed), 'is' if len(failed) == 1 else 'es'))
    parts.append('<footer class="paper">Generated by the NLP Suite Corpus Profiler with default '
                 'parameters. Figures and counts are produced automatically from the corpus; '
                 'interpretation is left to the reader. Full navigable index of every output: '
                 '<a href="%s">%s</a>.<br>%s</footer>'
                 % (_esc(report_basename), _esc(report_basename), _esc(run_config.get('footer', ''))))
    parts.append('</div></body></html>')

    with open(summary_path, 'w', encoding='utf-8') as fh:
        fh.write(''.join(parts))
    return summary_path
