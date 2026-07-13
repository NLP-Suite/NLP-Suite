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
    'counts':    'How big / how varied?  (Counts, measures & vocabulary)',
    'syntax':    'Grammar & structure — parts of speech  (Syntax)',
    'semantics': 'What do the words mean?  (Semantics)',
    'topics':    'What is it about?  (Topics)',
    'entities':  'Who, what, where, when  (Entities)',
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
    # NER (people/orgs/locations), gender, dialogue/quotes and normalized dates. Read from the shared
    # combined-CoreNLP cache if the parse phase produced it; otherwise run our own CoreNLP pass.
    picked = _cache_pick_any(c.get('_corenlp_files'),
                             'corenlp_ner', 'corenlp_gender', 'corenlp_quote', 'corenlp_normalized-date')
    if picked:
        print('>>> Entities: used the shared CoreNLP cache (%d files) -- no re-parse' % len(picked))
        return picked
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
    # parse POS to noun/verb lemma lists, then aggregate them UP to THREE complementary knowledge bases:
    #   WordNet  -- top-synset classes for nouns AND verbs (the interpretable "people vs things" view)
    #   VerbNet  -- verb CLASSES (verbs only)
    #   FrameNet -- semantic FRAMES (verbs and nouns)
    # Same lemma lists, three lenses on meaning. Each aggregation is guarded so one failing (e.g. an
    # NLTK corpus not downloaded) never loses the others.
    import semantic_aggregation_WordNet_util
    import semantic_aggregation_util
    cp, dt = c['chartPackage'], c['dataTransformation']

    # POS noun/verb lemma lists: prefer the shared combined-CoreNLP cache (CoreNLP_POS_lemma_Verbs /
    # _Nouns); else run our own POS pass.
    verb_file = noun_file = None
    cache = c.get('_corenlp_files')
    if cache:
        _vf = _cache_pick(cache, 'pos_lemma_verb', exclude=('chart', 'no_hyperlinks'))
        _nf = _cache_pick(cache, 'pos_lemma_noun', exclude=('chart', 'no_hyperlinks'))
        verb_file = _vf[0] if _vf else None
        noun_file = _nf[0] if _nf else None
        if verb_file or noun_file:
            print('>>> Semantics: used the shared CoreNLP POS cache -- no re-parse')
    if not (verb_file or noun_file):
        import Stanford_CoreNLP_util
        files = _files(Stanford_CoreNLP_util.CoreNLP_annotate(
            c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
            c['chartPackage'], c['dataTransformation'], ['POS'], False,
            c['language'], c['export_json_var'], c['memory_var'],
            c['document_length_var'], c['limit_sentence_length_var']))
        verb_file = files[0] if (len(files) > 0 and 'verb' in str(files[0]).lower()) else None
        noun_file = files[1] if (len(files) > 1 and 'noun' in str(files[1]).lower()) else None

    out = []
    if not (verb_file or noun_file):
        return out

    # WordNet: nouns and verbs -> top-synset classes
    for f, tag in ((verb_file, 'VERB'), (noun_file, 'NOUN')):
        if not f:
            continue
        try:
            out += _files(semantic_aggregation_WordNet_util.aggregate_GoingUP(
                '', f, c['outputDir'], c['config_filename'], tag, False, cp, dt, c['language']))
        except Exception as e:
            print('Corpus Profiler: WordNet %s aggregation skipped: %s' % (tag, e))

    # VerbNet (verbs only) + FrameNet (verbs), then FrameNet (nouns)
    if verb_file:
        for agg, name in ((semantic_aggregation_util.aggregate_VerbNet, 'VerbNet'),
                          (semantic_aggregation_util.aggregate_FrameNet, 'FrameNet')):
            try:
                out += _files(agg(verb_file, c['outputDir'], 'VERB', cp, dt))
            except Exception as e:
                print('Corpus Profiler: %s VERB aggregation skipped: %s' % (name, e))
    if noun_file:
        try:
            out += _files(semantic_aggregation_util.aggregate_FrameNet(
                noun_file, c['outputDir'], 'NOUN', cp, dt))
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
        c['window'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation'],
        'Plot word vectors', '2D', False, 200, '', True, True, c['config_filename'])
    return _files(out)


# ---- syntax: parts-of-speech distribution (nouns, verbs, adjectives, adverbs, pronouns) via Stanza POS ----
def _run_pos_stats(c):
    import Stanza_util
    out = Stanza_util.Stanza_annotate(
        c['config_filename'], c['inputFilename'], c['inputDir'], c['outputDir'], False,
        c['chartPackage'], c['dataTransformation'], ['All POS'], False,
        [c['language']], c['memory_var'], c['document_length_var'], c['limit_sentence_length_var'])
    return list(dict.fromkeys(_files(out)))   # Stanza returns the file once per doc; dedupe


# ---- narrative: SVO (CoreNLP) + SRL (transformer; self-skips if its env isn't installed) ----
def _run_svo(c):
    # Subject-Verb-Object triples via the CoreNLP 'SVO' annotator. Prefer the shared CoreNLP cache.
    picked = _cache_pick_any(c.get('_corenlp_files'), 'corenlp_svo')
    if picked:
        print('>>> Narrative/SVO: used the shared CoreNLP cache (%d files) -- no re-parse' % len(picked))
        return picked
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


# ---- character movement in space: Stanza tracks each character's locations -> animated migration map.
#      The map geocodes only DISTINCT locations (bounded); we further CAP to the 40 most frequent so an
#      unattended run on a big corpus can't stall on hundreds of Nominatim calls. ----
def _run_character_movement(c):
    import charts_util
    files = list(c.get('_ner_track_files') or [])   # shared NER location pass, if the parse phase primed it
    if files:
        print('>>> Characters/movement: used the shared NER location cache -- no re-parse')
    else:
        import NER_location_tracking_util
        files = _files(NER_location_tracking_util.main(
            c['inputFilename'], c['inputDir'], c['outputDir'], c['chartPackage'], c['dataTransformation']))
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
            c['inputFilename'], c['inputDir'], c['outputDir'], c['chartPackage'], c['dataTransformation']))
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
    'line_length':      dict(category='counts', kind='batch', run=_run_line_length,
                             label='Line length'),
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
    'hapax':            dict(category='counts', kind='batch', run=_run_hapax,
                             label='Hapax legomena (once-occurring words)'),
    'unusual_words':    dict(category='counts', kind='batch', run=_run_unusual_words,
                             label='Unusual words (via NLTK)'),
    'abstract_concrete': dict(category='counts', kind='batch', run=_run_abstract_concrete,
                             label='Abstract / concrete vocabulary'),
    'iconic':           dict(category='counts', kind='batch', run=_run_iconic,
                             label='Iconic vocabulary'),
    'capital_words':    dict(category='counts', kind='batch', run=_run_word_shape('capital'),
                             label='Words with capital initial (proper nouns)'),
    'language_detection': dict(category='counts', kind='batch', run=_run_language_detection,
                             label='Language detection'),
    # --- entities ---
    'entities_all':     dict(category='entities', kind='batch', run=_run_entities_all,
                             label='People, organizations, locations, gender, dates, dialogue (CoreNLP)'),
    # --- spatial: a quick geocodable-space snapshot RUNS in batch (proportional-symbol map; Google if a
    #     geocode key is configured, else Nominatim/folium). Full control (geocoder choice, API key,
    #     Google Earth / folium / distances, manual review) stays in the GIS GUI; symbolic space its GUI. ---
    'spatial_map':      dict(category='spatial', kind='batch', run=_run_spatial_map,
                             label='Geocodable space — proportional-symbol map of corpus locations (Nominatim/Google)'),
    'spatial_gis':      dict(category='spatial', kind='gui', gui_script='GIS_main.py',
                             label='Full geocoding & mapping — geocoder choice, API key, Google Earth / folium / distances  (opens GIS GUI)'),
    'spatial_symbolic': dict(category='spatial', kind='gui', gui_script='GIS_symbolic_main.py',
                             label='Symbolic space — narrative / gendered space typology  (opens Symbolic Space GUI)'),
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


def _prime_parse_cache(ctx, selected):
    ctx['_corenlp_files'] = None
    ctx['_ner_track_files'] = None
    sel = set(selected)

    # one combined CoreNLP pass covering every selected CoreNLP dimension
    annotators = []
    if 'entities_all' in sel:
        annotators += ['NER', 'gender', 'quote', 'normalized-date']
    if 'semantic_classes' in sel:
        annotators += ['POS']
    if 'narrative_svo' in sel:
        annotators += ['SVO']
    if len(annotators) >= 2:   # only worth combining when 2+ CoreNLP dimensions are on
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

    # one NER location-tracking pass shared by Spatial + Characters-movement (was run twice)
    if ('spatial_map' in sel) or ('character_movement' in sel):
        try:
            import NER_location_tracking_util
            print('>>> Corpus Profiler: ONE NER location pass shared by Spatial + Characters-movement')
            ctx['_ner_track_files'] = _files(NER_location_tracking_util.main(
                ctx['inputFilename'], ctx['inputDir'], ctx['outputDir'],
                ctx['chartPackage'], ctx['dataTransformation']))
        except Exception as e:
            print('Corpus Profiler: shared NER location pass failed (%s); dimensions will parse individually' % e)
            ctx['_ner_track_files'] = None


def run_profile(ctx, selected):
    _prime_parse_cache(ctx, selected)   # parse once, cache; runners read the cache (or fall back)
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
            # rough sentence count: runs of end-of-sentence punctuation. Cheap and parser-free; the exact
            # count comes from the Statistics analysis, this is just for the header/abstract averages.
            n_sents += len(re.findall(r'[.!?]+', text))
        except Exception:
            pass
    return dict(documents=n_docs, words=n_words, characters=n_chars, sentences=n_sents)


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
    'counts':     'How big and how varied is the corpus? The profiler measured its size and spread, and looked '
                  'at vocabulary richness, frequency, word shape and document similarity.',
    'syntax':     'How is the language built? Every word was POS-tagged, so the corpus can be read as a '
                  'distribution of parts of speech — nouns, verbs, adjectives, adverbs, pronouns.',
    'semantics':  'What do the words mean? Nouns and verbs were aggregated up to three knowledge bases — '
                  'WordNet classes, VerbNet verb classes and FrameNet frames — and the most frequent words '
                  'were embedded with BERT into a 2-D t-SNE semantic map.',
    'topics':     'What is the corpus about? Topics were surveyed.',
    'entities':   'Who, what, where and when? People, organizations, locations, gender and dates were extracted.',
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
    # Counts and Vocabulary are one merged dimension now. Report them together but, when BOTH have
    # findings, label the two sub-groups with bold sub-headings so the reader can still tell them apart.
    counts = _interp_counts(files)
    vocab = _interp_vocabulary(files) + _interp_tfidf_similarity(files)
    if counts and vocab:
        return ([_SUBHEAD + 'Counts & measures'] + counts +
                [_SUBHEAD + 'Vocabulary'] + vocab)
    return counts + vocab


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
        out = os.path.join(outputDir, 'NLP_corpus_wordcloud.png')
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
    abstract = (
        'This report profiles the corpus <b>%s</b>, comprising <b>%s</b> document%s totaling '
        '<b>%s</b> words (%s characters), an average of <b>%s</b> words and <b>%s</b> sentences per document. '
        'The Corpus Profiler ran <b>%d</b> automated analys%s across <b>%d</b> dimension%s — %s — '
        'producing <b>%s</b> output file%s. '
        '<span style="color:#c1121f;font-weight:700">The findings are summarized below; every figure '
        'links to the source data, and the full navigable index of all outputs is available in the '
        '<a href="%s" style="color:inherit">companion report</a>.</span>'
        % (_esc(corpus_name), _fmt(n_docs), '' if n_docs == 1 else 's',
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
        parts.append('<section class="dim"><h2 class="dim"><span class="num">%d</span>%s</h2>'
                     % (sec_no, _esc(CATEGORY_TITLE[cat])))
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
            # links inherit the red so the whole how-to-open line reads as one emphasized pointer
            links = ' &nbsp;·&nbsp; '.join('<a href="%s" style="color:inherit">▶&nbsp;%s</a>'
                                           % (_esc(_rel(h, report_dir)), _esc(_humanize_file(h)))
                                           for h in html_charts[:6])
            parts.append('<p class="interactive" style="color:#c1121f;font-weight:700">'
                         '<b>Interactive charts</b> (open in browser): %s</p>' % links)

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
        '<section class="dim"><h2 class="dim"><span class="num">+</span>Going further — statistics on '
        'these results</h2>'
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
