# Config-aware BASIC NLP layer for the NLP Suite.
#
# One place that performs the *basic* NLP operations - tokenizing, lemmatizing and POS tagging -
# using the package the user selected for "Basic functions (tokenizer/lemmatizer/POS)" in
# NLP_default_package_language_config.csv (read via config_util.read_NLP_package_language_config()
# as `basics_package`: 'spaCy' or 'Stanza'). Neither package runs a dependency parse here, so this
# is the FAST path (no full CoNLL parse) and it finally honors the user's choice instead of
# hard-coding Stanza.
#
# Public API:
#   basic_nlp(text, package=None, language=None) -> [(surface, lemma, POS), ...]
#       POS is the Penn/XPOS tag (NN, NNS, VBD, ...) so callers can filter NN*/VB* like a CoNLL table.
#   basic_nlp_many(texts, package=None, language=None) -> [[(surface, lemma, POS), ...], ...]
#       the same, for many texts in ONE batched call (one result list per text, in order)
#   basic_nlp_lemmas(text, ...) -> [(surface, lemma), ...]   (convenience)
#
# Lazy imports (stanza/spaCy loaded only when actually used) keep this module importable for tests.

import tkinter.messagebox as mb

# language name (as stored in the config) -> ISO 639-1 code used by both Stanza and spaCy models
_LANG_CODE = {
    'english': 'en', 'italian': 'it', 'spanish': 'es', 'french': 'fr', 'german': 'de',
    'portuguese': 'pt', 'dutch': 'nl', 'russian': 'ru', 'chinese': 'zh', 'arabic': 'ar',
}

_stanza_pipe = {}   # lang -> stanza.Pipeline (cached)
_spacy_nlp = {}     # lang -> spaCy nlp (cached)


def _lang_code(language):
    if not language:
        return 'en'
    key = str(language).strip().lower()
    return _LANG_CODE.get(key, key[:2] if len(key) >= 2 else 'en')


def _read_config_basics():
    """Return (basics_package, language) from the NLP setup config; defaults to ('Stanza', 'English')."""
    try:
        import config_util
        vals = config_util.read_NLP_package_language_config()
        # (error, package, parsers, basics_package, language, ...)
        return (vals[3] or 'Stanza'), (vals[4] or 'English')
    except Exception:
        return 'Stanza', 'English'


def _resolve_package_lang(package, language):
    """Fill a missing package/language from the config; return (package, ISO language code)."""
    if package is None or language is None:
        cfg_pkg, cfg_lang = _read_config_basics()
        package = cfg_pkg if package is None else package
        language = cfg_lang if language is None else language
    return package, _lang_code(language)


def _warn_basic_nlp_failure(package, lang, e):
    mb.showwarning(title='Basic NLP',
                   message="The basic NLP package '%s' (%s) could not tokenize/lemmatize/POS-tag the "
                           "text:\n\n%s\n\nCheck the Setup NLP package and language options." %
                           (package, lang, e))


def _stanza_pipeline(lang):
    import stanza
    if lang not in _stanza_pipe:
        try:
            _stanza_pipe[lang] = stanza.Pipeline(lang=lang, processors='tokenize, pos, lemma',
                                                 verbose=False)
        except Exception:
            # models not present yet - download once, then retry
            stanza.download(lang, processors='tokenize, pos, lemma', verbose=False)
            _stanza_pipe[lang] = stanza.Pipeline(lang=lang, processors='tokenize, pos, lemma',
                                                 verbose=False)
    return _stanza_pipe[lang]


def _stanza_doc_tuples(doc):
    out = []
    for sentence in doc.sentences:
        for w in sentence.words:
            out.append(((w.text or ''), (w.lemma or w.text or ''), (w.xpos or w.upos or '')))
    return out


def _stanza_basic(text, lang):
    return _stanza_doc_tuples(_stanza_pipeline(lang)(text))


def _stanza_basic_many(texts, lang):
    # bulk_process wraps each text as its own Document, so no sentence ever spans two texts
    return [_stanza_doc_tuples(doc) for doc in _stanza_pipeline(lang).bulk_process(texts)]


def _spacy_model(lang):
    import spacy
    if lang not in _spacy_nlp:
        model = lang + '_core_web_sm'
        try:
            _spacy_nlp[lang] = spacy.load(model)
        except OSError:
            import sys
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'spacy', 'download', model])
            _spacy_nlp[lang] = spacy.load(model)
    return _spacy_nlp[lang]


def _spacy_doc_tuples(doc):
    return [((t.text or ''), (t.lemma_ or t.text or ''), (t.tag_ or t.pos_ or '')) for t in doc]


def _spacy_basic(text, lang):
    return _spacy_doc_tuples(_spacy_model(lang)(text))


def _spacy_basic_many(texts, lang):
    return [_spacy_doc_tuples(doc) for doc in _spacy_model(lang).pipe(texts)]


def basic_nlp(text, package=None, language=None):
    """Tokenize + lemmatize + POS-tag `text` with the user's configured Basic-functions package
    (spaCy or Stanza). Returns [(surface, lemma, POS), ...]; POS is the Penn/XPOS tag (NN*/VB*-style).
    Returns [] (and warns) if the package can't run, so callers can fall back gracefully."""
    package, lang = _resolve_package_lang(package, language)
    try:
        if 'spacy' in str(package).lower():
            return _spacy_basic(text, lang)
        return _stanza_basic(text, lang)   # Stanza is the default basic package
    except Exception as e:
        _warn_basic_nlp_failure(package, lang, e)
        return []


def basic_nlp_many(texts, package=None, language=None):
    """basic_nlp() over a list of texts in ONE batched call. Returns one [(surface, lemma, POS), ...] list per
    text, in input order. Each text is still processed as its own document, so the output matches calling
    basic_nlp() on each text separately; it is faster because the tagger works through batches instead of
    starting over for every text. Blank texts give []. On failure it warns once and returns [] for every text."""
    texts = [str(t) for t in texts]
    results = [[] for _ in texts]
    todo = [i for i, t in enumerate(texts) if t.strip()]
    if not todo:
        return results
    package, lang = _resolve_package_lang(package, language)
    batch = [texts[i] for i in todo]
    try:
        if 'spacy' in str(package).lower():
            tagged = _spacy_basic_many(batch, lang)
        else:
            tagged = _stanza_basic_many(batch, lang)   # Stanza is the default basic package
    except Exception as e:
        _warn_basic_nlp_failure(package, lang, e)
        return results
    for i, tuples in zip(todo, tagged, strict=True):
        results[i] = tuples
    return results


def basic_nlp_lemmas(text, package=None, language=None):
    """Convenience: [(surface, lemma), ...] (drops POS)."""
    return [(s, l) for (s, l, _p) in basic_nlp(text, package, language)]
