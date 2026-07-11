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
CATEGORY_ORDER = ['counts', 'vocabulary', 'syntax', 'semantics',
                  'topics', 'entities', 'spatial', 'narrative', 'sentiment', 'arcs']

CATEGORY_TITLE = {
    'counts':    'How big / how varied?  (Counts & measures)',
    'vocabulary': "What's the vocabulary like?  (Vocabulary)",
    'syntax':    'Grammar & structure  (Syntax)',
    'semantics': 'What do the words mean?  (Semantics)',
    'topics':    'What is it about?  (Topics)',
    'entities':  'Who, what, where, when  (Entities)',
    'spatial':   'Where does it all happen?  (geocodable and symbolic space)',
    'narrative': 'Who did what to whom?  (Narrative)',
    'sentiment': 'How does it feel?  (Sentiment)',
    'arcs':      'How do characters feel over the story?  (Character emotion arcs)',
}


# ---------------------------------------------------------------------------------------------
# Batch runners. Each takes the shared context dict `c` and returns a list of output file paths.
# They lazily import the underlying util module so this file imports cleanly for report testing.
# Signatures are taken verbatim from the working calls in each analysis GUI's run().
# ---------------------------------------------------------------------------------------------
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

def _run_sentence_length(c):
    import statistics_txt_util
    return _files(statistics_txt_util.compute_sentence_length(
        c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename'],
        c['chartPackage'], c['dataTransformation']))

def _run_line_length(c):
    import statistics_txt_util
    return _files(statistics_txt_util.compute_line_length(
        c['window'], c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation']))

def _run_language_detection(c):
    import file_spell_checker_util
    return _files(file_spell_checker_util.language_detection(
        c['window'], c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename'],
        False, c['chartPackage'], c['dataTransformation']))


# ---- vocabulary ---------------------------------------------------------------------------
def _run_yule(c):
    import statistics_txt_util
    return _files(statistics_txt_util.yule(
        c['window'], c['inputFilename'], c['inputDir'], c['outputDir'], c['config_filename']))

def _run_word_shape(keyword):
    # process_words(window, configFileName, inputFilename, inputDir, outputDir, openOutputFiles,
    #   chartPackage, dataTransformation, processType='', language='English', ...) -- processType is
    #   the menu keyword it switches on ('Hapax legomena', 'capital', 'Vowel', 'Word length', ...)
    def runner(c):
        import statistics_txt_util
        return _files(statistics_txt_util.process_words(
            c['window'], c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'],
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
def _run_entities_all(c):
    # one CoreNLP pass yields NER (people/orgs/locations), gender, dialogue/quotes and normalized dates
    import Stanford_CoreNLP_util
    NER_list = ['PERSON', 'ORGANIZATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY', 'LOCATION']
    out = Stanford_CoreNLP_util.CoreNLP_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation'],
        ['NER', 'gender', 'quote', 'normalized-date'], False,
        c['language'], c['export_json_var'], c['memory_var'],
        c['document_length_var'], c['limit_sentence_length_var'], NERs=NER_list)
    return _files(out)


# ---- semantics (English + WordNet) --------------------------------------------------------
def _run_semantic_classes(c):
    # parse POS, then aggregate nouns & verbs UP to their WordNet top-synset classes
    import Stanford_CoreNLP_util
    import semantic_aggregation_WordNet_util
    files = Stanford_CoreNLP_util.CoreNLP_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation'], ['POS'], False,
        c['language'], c['export_json_var'], c['memory_var'],
        c['document_length_var'], c['limit_sentence_length_var'])
    out = []
    if files:
        pairs = []
        if len(files) > 0 and 'verb' in str(files[0]).lower():
            pairs.append((files[0], 'VERB'))
        if len(files) > 1 and 'noun' in str(files[1]).lower():
            pairs.append((files[1], 'NOUN'))
        for f, tag in pairs:
            r = semantic_aggregation_WordNet_util.aggregate_GoingUP(
                '', f, c['outputDir'], c['config_filename'], tag,
                False, c['chartPackage'], c['dataTransformation'], c['language'])
            out += _files(r)
    return out


# ---- narrative: SVO (CoreNLP) + SRL (transformer; self-skips if its env isn't installed) ----
def _run_svo(c):
    # Subject-Verb-Object triples via the CoreNLP 'SVO' annotator, run with defaults
    import Stanford_CoreNLP_util
    out = Stanford_CoreNLP_util.CoreNLP_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation'], ['SVO'], False,
        c['language'], c['export_json_var'], c['memory_var'],
        c['document_length_var'], c['limit_sentence_length_var'])
    return _files(out)


def _run_srl(c):
    # SRL needs the isolated transformer-srl env + model; skip cleanly if not installed
    import SRL_util
    if not SRL_util.is_available():
        return []
    import GUI_util
    return _files(SRL_util.run_SRL(GUI_util.window, c['inputFilename'], c['inputDir'],
                                   c['outputDir'], c['chartPackage'], c['dataTransformation']))


# ---- sentiment: Stanza neural sentiment (a real model, not a dictionary; already installed) ---
def _run_sentiment(c):
    import Stanza_util
    out = Stanza_util.Stanza_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation'], ['sentiment'], False,
        [c['language']], c['memory_var'], c['document_length_var'], c['limit_sentence_length_var'])
    return _files(out)


# ---- topics: Gensim LDA (pure Python). force=True bypasses the "needs 50+ files" advisory so the
#      unattended sweep can still run it; on a small corpus the topics are indicative, not authoritative. ---
def _run_topics(c):
    import topic_modeling_gensim_util
    return _files(topic_modeling_gensim_util.run_Gensim(
        c['window'], c['inputDir'], c['outputDir'], c['config_filename'],
        10, True, True, False, False, False,
        c['chartPackage'], c['dataTransformation'], force=True))


# ---- character emotion arcs: Stanza NER + NRC's 8 emotions, traced per character across the story ---
def _run_character_arcs(c):
    import character_emotion_arcs_util
    return _files(character_emotion_arcs_util.main(
        c['inputFilename'], c['inputDir'], c['outputDir'], c['chartPackage'], c['dataTransformation']))


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
    'line_length':      dict(category='counts', kind='batch', run=_run_line_length,
                             label='Line length'),
    # --- vocabulary (a curated SNAPSHOT; the full ~20-option menu lives in the Style Analysis GUI,
    #     which the report/help points to). Sourced from style_analysis_main.run(). ---
    'yule':             dict(category='vocabulary', kind='batch', run=_run_yule,
                             label="Vocabulary richness (word type/token ratio or Yule's K)"),
    'lexical_diversity': dict(category='vocabulary', kind='batch', run=_run_lexical_diversity,
                             label='Lexical diversity (TTR, MTLD, vocd-D)'),
    'word_frequency':   dict(category='vocabulary', kind='batch', run=_run_word_frequency,
                             label="Word frequency distribution (Zipf's Law)"),
    'tfidf':            dict(category='vocabulary', kind='batch', run=_run_tfidf,
                             label='TF-IDF (most distinctive words per document)'),
    'hapax':            dict(category='vocabulary', kind='batch', run=_run_hapax,
                             label='Hapax legomena (once-occurring words)'),
    'unusual_words':    dict(category='vocabulary', kind='batch', run=_run_unusual_words,
                             label='Unusual words (via NLTK)'),
    'abstract_concrete': dict(category='vocabulary', kind='batch', run=_run_abstract_concrete,
                             label='Abstract / concrete vocabulary'),
    'iconic':           dict(category='vocabulary', kind='batch', run=_run_iconic,
                             label='Iconic vocabulary'),
    'capital_words':    dict(category='vocabulary', kind='batch', run=_run_word_shape('capital'),
                             label='Words with capital initial (proper nouns)'),
    'language_detection': dict(category='vocabulary', kind='batch', run=_run_language_detection,
                             label='Language detection'),
    # --- entities ---
    'entities_all':     dict(category='entities', kind='batch', run=_run_entities_all,
                             label='People, organizations, locations, gender, dates, dialogue (CoreNLP)'),
    # --- spatial (geocoding is network-heavy & rate-limited -> pointers, not batch) ---
    'spatial_gis':      dict(category='spatial', kind='gui', gui_script='GIS_main.py',
                             label='Geocodable space — geocode & map corpus locations  (opens GIS GUI)'),
    'spatial_symbolic': dict(category='spatial', kind='gui', gui_script='GIS_symbolic_main.py',
                             label='Symbolic space — narrative / gendered space typology  (opens Symbolic Space GUI)'),
    # --- semantics (snapshot: WordNet noun/verb classes; deeper tools via the Semantic GUI) ---
    'semantic_classes': dict(category='semantics', kind='batch', run=_run_semantic_classes,
                             label='Noun & verb classes (WordNet top synsets)'),
    'semantics_more':   dict(category='semantics', kind='gui', gui_script='semantic_analysis_main.py',
                             label='WSD · word embeddings · semantic similarity · nominalization  (opens Semantic Analysis GUI)'),
    # --- syntax (full parse + CoNLL analyses live in the analyzer GUI) ---
    'syntax_gui':       dict(category='syntax', kind='gui', gui_script='CoNLL_table_analyzer_main.py',
                             label='POS · dependency · clause · N/V/Adj/Adv · function words · complexity · readability'),
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
                             label='Coreference · dialogue · 5 Ws  (opens SVO GUI)'),
    # --- sentiment (VADER runs by default; other engines open from the Sentiment GUI) ---
    'sentiment_stanza': dict(category='sentiment', kind='batch', run=_run_sentiment,
                             label='Sentiment (Stanza)'),
    'sentiment_more':   dict(category='sentiment', kind='gui', gui_script='sentiment_analysis_main.py',
                             label='BERT · spaCy · VADER · NRC · SentiWordNet  (opens Sentiment GUI)'),
    # --- arcs (character emotion arcs: Stanza NER + NRC 8-emotion scoring, per character over the story) ---
    # Batch-only dimension -- no GUI pointer. (Whole-narrative "shape of stories" is heavy BERT+clustering
    # and GUI-coupled, like topics; it stays in the Sentiment GUI and is mentioned in this row's HELP.)
    'character_arcs':   dict(category='arcs', kind='batch', run=_run_character_arcs,
                             label='Character emotion arcs (NRC 8 emotions, per character across the story)'),
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
def run_profile(ctx, selected):
    results = []
    for aid in selected:
        entry = REGISTRY.get(aid)
        if entry is None:
            continue
        rec = dict(id=aid, category=entry['category'], label=entry['label'],
                   kind=entry['kind'], files=[], error='', gui_script=entry.get('gui_script', ''))
        if entry['kind'] == 'batch':
            try:
                rec['files'] = entry['run'](ctx) or []
            except Exception as e:
                # no silent failure: record the error; the report shows it; the profile continues
                rec['error'] = str(e)
                print('Corpus Profiler: analysis "%s" failed: %s' % (aid, e))
        # kind == 'gui': nothing to run -- the report surfaces it as an "open the tool" pointer
        results.append(rec)
    return results


# ---------------------------------------------------------------------------------------------
# Corpus header stats -- cheap counts for the report header. Reads the raw txt corpus directly
# so it works even if no analysis produced a statistics file.
# ---------------------------------------------------------------------------------------------
def corpus_header_stats(inputFilename, inputDir):
    import glob
    paths = []
    if inputDir:
        paths = sorted(glob.glob(os.path.join(inputDir, '*.txt')))
    elif inputFilename:
        paths = [inputFilename]
    n_docs = len(paths)
    n_words = 0
    n_chars = 0
    for p in paths:
        try:
            with open(p, encoding='utf-8', errors='ignore') as fh:
                text = fh.read()
            n_words += len(text.split())
            n_chars += len(text)
        except Exception:
            pass
    return dict(documents=n_docs, words=n_words, characters=n_chars)


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

    # header stat tiles
    tiles = [('documents', 'documents'), ('words', 'words'), ('characters', 'characters')]
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
    'counts':     'How big and how varied is the corpus? The profiler measured its size and spread.',
    'vocabulary': 'What is the vocabulary like? The profiler looked at richness, frequency and word shape.',
    'syntax':     'How is the language structured? Grammar and dependency structure were examined.',
    'semantics':  'What do the words mean? Nouns and verbs were aggregated up to their WordNet classes.',
    'topics':     'What is the corpus about? Topics were surveyed.',
    'entities':   'Who, what, where and when? People, organizations, locations, gender and dates were extracted.',
    'spatial':    'Where does it all happen? Both geocodable and symbolic (narrative) space were considered.',
    'narrative':  'Who did what to whom? Subject-Verb-Object triples and semantic roles were derived.',
    'sentiment':  'How does the corpus feel? Sentiment was scored with a neural model.',
    'arcs':       'How do the people in the story feel, and how does that feeling rise and fall? '
                  'NRC’s eight emotions were traced per character across the narrative.',
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


def _interp_entities(files):
    import pandas as pd
    findings = []
    f = _find(files, 'ner_all_ner', exclude=('bydoc', 'chart', 'group', 'no_hyperlinks', 'stats'))
    if f:
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
    return findings


def _interp_narrative(files):
    import pandas as pd
    findings = []
    fs = _find(files, 'svo', exclude=('sunburst', 'treemap', 'form', 'chart', 'bydoc'))
    if fs:
        df = _read_csv(fs)
        if df is not None:
            findings.append('Subject–Verb–Object extraction produced %s triples.' % _thousands(len(df)))
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
            'Topic modeling needs many documents for authoritative results — on a small corpus these are indicative.']


_EIGHT_EMOTIONS = ('Anger', 'Anticipation', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Trust')


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
    return findings


def _interpret(category, files):
    """Dispatch to the per-category interpreter; always returns a (possibly empty) list of sentences."""
    fn = {'counts': _interp_counts, 'vocabulary': _interp_vocabulary, 'entities': _interp_entities,
          'semantics': _interp_semantics, 'narrative': _interp_narrative,
          'sentiment': _interp_sentiment, 'arcs': _interp_arcs, 'topics': _interp_topics}.get(category)
    if not fn:
        return []
    try:
        return [s for s in fn(files) if s]
    except Exception as e:
        print('Corpus Profiler: interpretation for "%s" skipped: %s' % (category, e))
        return []


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
    avg_words = int(round(n_words / n_docs)) if n_docs else 0
    total_files = sum(len(r['files']) for r in results)
    ran = [r for r in results if r.get('kind') == 'batch' and not r.get('error')]
    failed = [r for r in results if r.get('error')]

    def _fmt(n):
        return '{:,}'.format(n)

    # ---- abstract (templated from the real counts) ----
    dims = ', '.join(CATEGORY_TITLE[c].split('  ')[0].rstrip('?').strip().lower() for c in cats_present)
    abstract = (
        'This report profiles the corpus <b>%s</b>, comprising <b>%s</b> document%s totaling '
        '<b>%s</b> words (%s characters), an average of <b>%s</b> words per document. '
        'The Corpus Profiler ran <b>%d</b> automated analys%s across <b>%d</b> dimension%s — %s — '
        'producing <b>%s</b> output file%s. The findings are summarized below; every figure links to '
        'the source data, and the full navigable index of all outputs is available in the '
        '<a href="%s">companion report</a>.'
        % (_esc(corpus_name), _fmt(n_docs), '' if n_docs == 1 else 's',
           _fmt(n_words), _fmt(n_chars), _fmt(avg_words),
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
</style></head><body><div class="wrap">
""" % _esc(corpus_name))

    parts.append('<header class="paper"><div class="eyebrow">Corpus Profile · paper-style summary</div>'
                 '<h1>%s</h1><div class="byline">%s</div></header>'
                 % (_esc(corpus_name), _esc(run_config.get('subtitle', ''))))

    parts.append('<div class="abstract"><span class="lead">Abstract</span>%s</div>' % abstract)

    # by-the-numbers strip
    kpis = [(_fmt(n_docs), 'documents'), (_fmt(n_words), 'words'),
            (_fmt(avg_words), 'avg words / document'), (_fmt(total_files), 'output files')]
    parts.append('<div class="figures-strip">')
    for val, lab in kpis:
        parts.append('<div class="kpi"><b>%s</b><span>%s</span></div>' % (_esc(val), _esc(lab)))
    parts.append('</div>')

    # ---- numbered sections, one per dimension that produced results ----
    fig_no = 0
    sec_no = 0
    MAX_FIG_PER_SECTION = 4
    for cat in cats_present:
        recs = by_cat[cat]
        sec_no += 1
        parts.append('<section class="dim"><h2 class="dim"><span class="num">%d</span>%s</h2>'
                     % (sec_no, _esc(CATEGORY_TITLE[cat])))
        parts.append('<p class="lead-p">%s</p>' % _esc(_CATEGORY_LEAD.get(cat, '')))

        # INTERPRETATION: read this dimension's output CSVs and state what they say, in prose
        cat_files = []
        for r in recs:
            cat_files += r.get('files', [])
        for _finding in _interpret(cat, cat_files):
            parts.append('<p class="finding">%s</p>' % _esc(_finding))

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

        # embed up to MAX_FIG_PER_SECTION charts as figures
        for img in all_imgs[:MAX_FIG_PER_SECTION]:
            fig_no += 1
            parts.append('<figure><a href="%s"><img src="%s" alt="%s" loading="lazy"></a>'
                         '<figcaption><span class="fnum">Figure %d.</span> %s</figcaption></figure>'
                         % (_esc(_rel(img, report_dir)), _esc(_rel(img, report_dir)),
                            _esc(_humanize_file(img)), fig_no, _esc(_humanize_file(img))))
        if len(all_imgs) > MAX_FIG_PER_SECTION:
            parts.append('<p class="note">+%d more chart%s for this dimension in the '
                         '<a href="%s">full report</a>.</p>'
                         % (len(all_imgs) - MAX_FIG_PER_SECTION,
                            '' if len(all_imgs) - MAX_FIG_PER_SECTION == 1 else 's',
                            _esc(report_basename)))

        # source-data links (csv/xlsx) + interactive artifacts
        srcs = all_data + all_inter
        if srcs:
            links = ' · '.join('<a href="%s">%s</a>' % (_esc(_rel(s, report_dir)), _esc(os.path.basename(s)))
                               for s in srcs[:12])
            more = ('  (+%d more)' % (len(srcs) - 12)) if len(srcs) > 12 else ''
            parts.append('<div class="sources"><b>Source data:</b> %s%s</div>' % (links, _esc(more)))

        # GUI-only dimensions (geocoding, topics, deeper tools) -> honest pointer
        if gui_ptrs and not all_imgs and not srcs:
            parts.append('<p class="note">This dimension is explored interactively — open the '
                         '<b>%s</b> tool from the NLP Suite menu.</p>' % _esc(', '.join(gui_ptrs)))

        # failures surfaced, never swallowed
        for lab, err in errs:
            parts.append('<p class="note err">%s could not be completed: %s</p>'
                         % (_esc(lab), _esc(err)))

        parts.append('</section>')

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
