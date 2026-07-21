# Written by Roberto Franzosi & Claude
# Config-aware NLP parser adapter for the NLP Suite.
#
# WHY: several older tools hardcoded the Java Stanford CoreNLP wrapper
# (nlp = StanfordCoreNLP(dir); nlp.pos_tag(text); nlp.ner(text); nlp.word_tokenize(text)),
# which forced every user to install CoreNLP even after the Suite moved to Stanza/spaCy.
#
# WHAT: ConfigParser is a drop-in replacement for that StanfordCoreNLP object. It exposes the
# SAME pos_tag() / ner() / word_tokenize() / close() API, but is backed by whichever NLP package
# the user selected in the NLP Suite setup (Stanford CoreNLP / Stanza / spaCy), read from
# config_util.read_NLP_package_language_config(). Calling code therefore does not change at all.
#
# TWO THINGS MAKE IT DROP-IN:
#   1. POS is returned as PENN tags (Stanza word.xpos, spaCy token.tag_), so existing
#      `pos == 'NN' or pos == 'NNS'` style checks keep working. (Note: this deliberately does NOT
#      go through the Suite's CoNLL 'POS' column, which holds Universal POS for Stanza/spaCy.)
#   2. NER is mapped from the OntoNotes tags Stanza/spaCy emit to the CoreNLP-style tags the
#      legacy code checks: GPE/LOC -> LOCATION, ORG -> ORGANIZATION, PERSON/DATE unchanged.
#      BIOES prefixes (B-/I-/E-/S-) are stripped.
#
# Parser libraries are imported LAZILY, so a Stanza/spaCy user is never forced to install the
# Stanford CoreNLP wrapper (and vice versa).
#
# CAVEAT: entity RESULTS still differ by model -- e.g. Stanza may tag a newspaper name as LAW
# rather than ORG. That is model behaviour, not a bug; compare on a real corpus when switching.
#
# Validated end-to-end against real Stanza 1.10 and spaCy 3.4 (identical noun / PERSON /
# LOCATION / DATE output on the same text).

import config_util
import basic_NLP_util


class ConfigParser:
    """Drop-in, config-aware replacement for a StanfordCoreNLP object."""

    # OntoNotes entity types (Stanza / spaCy) -> the CoreNLP-style tags legacy code checks
    _NER_MAP = {'PERSON': 'PERSON', 'ORG': 'ORGANIZATION',
                'GPE': 'LOCATION', 'LOC': 'LOCATION', 'FAC': 'LOCATION', 'DATE': 'DATE'}

    def __init__(self, package, language, CoreNLPDir=''):
        p = (package or '').lower()
        self._corenlp = None
        self._pipe = None
        self._cache_text = None
        self._cache_doc = None
        if 'spacy' in p:
            self.kind = 'spacy'
            import spacy
            self._pipe = spacy.load(basic_NLP_util._lang_code(language) + '_core_web_sm')
        elif 'stanford' in p or 'corenlp' in p:
            self.kind = 'corenlp'
            from stanfordcorenlp import StanfordCoreNLP  # python wrapper for Stanford CoreNLP
            self._corenlp = StanfordCoreNLP(CoreNLPDir)
        else:  # Stanza is the NLP Suite's default Python parser
            self.kind = 'stanza'
            import stanza
            self._pipe = stanza.Pipeline(basic_NLP_util._lang_code(language),
                                         processors='tokenize,pos,ner', verbose=False)

    # cache the last parse so a pos_tag() + ner() pair on the same text only parses once
    def _doc(self, text):
        if text != self._cache_text:
            self._cache_text, self._cache_doc = text, self._pipe(text)
        return self._cache_doc

    def pos_tag(self, text):
        """[(word, PennPOS), ...] -- same shape as StanfordCoreNLP.pos_tag()."""
        if self.kind == 'corenlp':
            return self._corenlp.pos_tag(text)
        if self.kind == 'stanza':
            return [(w.text, w.xpos or '') for s in self._doc(text).sentences for w in s.words]
        return [(t.text, t.tag_) for t in self._doc(text)]  # spaCy tag_ = Penn

    def ner(self, text):
        """[(word, NERtag), ...] with CoreNLP-style tags; 'O' for non-entities."""
        if self.kind == 'corenlp':
            return self._corenlp.ner(text)
        out = []
        if self.kind == 'stanza':
            for s in self._doc(text).sentences:
                for t in s.tokens:
                    tag = t.ner.split('-')[-1] if (t.ner and t.ner != 'O') else 'O'  # strip BIOES
                    out.append((t.text, self._NER_MAP.get(tag, tag)))
        else:  # spaCy
            for t in self._doc(text):
                tag = t.ent_type_ or 'O'
                out.append((t.text, self._NER_MAP.get(tag, tag)))
        return out

    def word_tokenize(self, text):
        """[token, ...] -- same shape as StanfordCoreNLP.word_tokenize()."""
        if self.kind == 'corenlp':
            return self._corenlp.word_tokenize(text)
        if self.kind == 'stanza':
            return [w.text for s in self._doc(text).sentences for w in s.words]
        return [t.text for t in self._doc(text)]

    def close(self):
        if self._corenlp is not None:
            self._corenlp.close()


def configured_package_language():
    """(package, language) as selected in the NLP Suite setup; safe defaults if the config is unreadable."""
    try:
        cfg = config_util.read_NLP_package_language_config()
        package = cfg[1] if (cfg and len(cfg) > 1 and cfg[1]) else 'Stanford CoreNLP'
        language = cfg[4] if (cfg and len(cfg) > 4 and cfg[4]) else 'English'
        return package, language
    except Exception:
        return 'Stanford CoreNLP', 'English'


def requires_CoreNLP():
    """True when the CONFIGURED package is Stanford CoreNLP, i.e. the CoreNLP directory is needed.
    GUIs use this to stop demanding a CoreNLP install from Stanza/spaCy users."""
    package, _ = configured_package_language()
    p = package.lower()
    return ('stanford' in p) or ('corenlp' in p)


def get_parser(CoreNLPDir=''):
    """Convenience: build a ConfigParser for the configured package/language."""
    package, language = configured_package_language()
    return ConfigParser(package, language, CoreNLPDir)
