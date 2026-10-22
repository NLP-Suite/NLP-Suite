"""Unit tests for basic_NLP_util.basic_nlp_many, the batched form of basic_nlp.

The Stanza pipeline and spaCy model caches are filled with fakes, so no NLP library is loaded.
"""

from types import SimpleNamespace

import pytest

try:
    import basic_NLP_util
except (ImportError, SystemExit):  # pragma: no cover - defensive
    pytest.skip("basic_NLP_util dependencies not available", allow_module_level=True)


def _stanza_doc(text):
    # one sentence; each whitespace token is a word with lemma = lowercase and xpos = NN
    words = [SimpleNamespace(text=t, lemma=t.lower(), xpos="NN", upos="NOUN") for t in text.split()]
    return SimpleNamespace(sentences=[SimpleNamespace(words=words)])


class _FakeStanzaPipeline:
    def __init__(self):
        self.bulk_calls = []

    def __call__(self, text):
        return _stanza_doc(text)

    def bulk_process(self, texts):
        self.bulk_calls.append(list(texts))
        return [_stanza_doc(t) for t in texts]


@pytest.fixture
def fake_stanza(monkeypatch):
    pipe = _FakeStanzaPipeline()
    monkeypatch.setitem(basic_NLP_util._stanza_pipe, "en", pipe)
    return pipe


def test_many_matches_one_at_a_time(fake_stanza):
    texts = ["The Destruction began", "Nobody said anything"]
    many = basic_NLP_util.basic_nlp_many(texts, package="Stanza", language="English")
    single = [basic_NLP_util.basic_nlp(t, package="Stanza", language="English") for t in texts]
    assert many == single
    assert many[0] == [("The", "the", "NN"), ("Destruction", "destruction", "NN"), ("began", "began", "NN")]


def test_many_is_one_batched_call(fake_stanza):
    basic_NLP_util.basic_nlp_many(["a b", "c d", "e f"], package="Stanza", language="English")
    assert fake_stanza.bulk_calls == [["a b", "c d", "e f"]]


def test_blank_texts_keep_their_position(fake_stanza):
    result = basic_NLP_util.basic_nlp_many(["one", "", "   ", "two"], package="Stanza", language="English")
    assert result == [[("one", "one", "NN")], [], [], [("two", "two", "NN")]]
    assert fake_stanza.bulk_calls == [["one", "two"]]


def test_all_blank_skips_the_tagger(fake_stanza):
    assert basic_NLP_util.basic_nlp_many(["", " "], package="Stanza", language="English") == [[], []]
    assert fake_stanza.bulk_calls == []


def test_spacy_uses_pipe(monkeypatch):
    def token(t):
        return SimpleNamespace(text=t, lemma_=t.lower(), tag_="NN", pos_="NOUN")

    class FakeNlp:
        def __call__(self, text):
            return [token(t) for t in text.split()]

        def pipe(self, texts):
            return [self(t) for t in texts]

    monkeypatch.setitem(basic_NLP_util._spacy_nlp, "en", FakeNlp())
    texts = ["Big Decision", "small"]
    many = basic_NLP_util.basic_nlp_many(texts, package="spaCy", language="English")
    assert many == [basic_NLP_util.basic_nlp(t, package="spaCy", language="English") for t in texts]


def test_failure_warns_once_and_returns_empty_lists(monkeypatch):
    class Broken:
        def bulk_process(self, texts):
            raise RuntimeError("model missing")

    warnings = []
    monkeypatch.setitem(basic_NLP_util._stanza_pipe, "en", Broken())
    monkeypatch.setattr(basic_NLP_util.mb, "showwarning", lambda **kw: warnings.append(kw))
    assert basic_NLP_util.basic_nlp_many(["a", "b"], package="Stanza", language="English") == [[], []]
    assert len(warnings) == 1
