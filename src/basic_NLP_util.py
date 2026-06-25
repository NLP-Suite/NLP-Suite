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


def _stanza_basic(text, lang):
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
    doc = _stanza_pipe[lang](text)
    out = []
    for sentence in doc.sentences:
        for w in sentence.words:
            out.append(((w.text or ''), (w.lemma or w.text or ''), (w.xpos or w.upos or '')))
    return out


def _spacy_basic(text, lang):
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
    doc = _spacy_nlp[lang](text)
    return [((t.text or ''), (t.lemma_ or t.text or ''), (t.tag_ or t.pos_ or '')) for t in doc]


def basic_nlp(text, package=None, language=None):
    """Tokenize + lemmatize + POS-tag `text` with the user's configured Basic-functions package
    (spaCy or Stanza). Returns [(surface, lemma, POS), ...]; POS is the Penn/XPOS tag (NN*/VB*-style).
    Returns [] (and warns) if the package can't run, so callers can fall back gracefully."""
    if package is None or language is None:
        cfg_pkg, cfg_lang = _read_config_basics()
        package = cfg_pkg if package is None else package
        language = cfg_lang if language is None else language
    lang = _lang_code(language)
    try:
        if 'spacy' in str(package).lower():
            return _spacy_basic(text, lang)
        return _stanza_basic(text, lang)   # Stanza is the default basic package
    except Exception as e:
        mb.showwarning(title='Basic NLP',
                       message="The basic NLP package '%s' (%s) could not tokenize/lemmatize/POS-tag the "
                               "text:\n\n%s\n\nCheck the Setup NLP package and language options." %
                               (package, lang, e))
        return []


def basic_nlp_lemmas(text, package=None, language=None):
    """Convenience: [(surface, lemma), ...] (drops POS)."""
    return [(s, l) for (s, l, _p) in basic_nlp(text, package, language)]
