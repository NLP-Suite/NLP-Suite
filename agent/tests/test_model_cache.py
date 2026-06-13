import sys
import types

import model_cache
import pytest


@pytest.fixture(autouse=True)
def clear_cache():
    model_cache._CACHE.clear()
    yield
    model_cache._CACHE.clear()


@pytest.fixture
def fake_stanza(monkeypatch):
    calls = []

    def pipeline(**kwargs):
        calls.append(kwargs)
        return object()

    monkeypatch.setitem(sys.modules, "stanza", types.SimpleNamespace(Pipeline=pipeline))
    return calls


def test_same_args_return_same_object(fake_stanza):
    first = model_cache.get_stanza_pipeline(lang="en", processors="tokenize")
    second = model_cache.get_stanza_pipeline(lang="en", processors="tokenize")
    assert first is second
    assert len(fake_stanza) == 1


def test_different_processors_construct_again(fake_stanza):
    first = model_cache.get_stanza_pipeline(lang="en", processors="tokenize")
    second = model_cache.get_stanza_pipeline(lang="en", processors="tokenize,lemma")
    assert first is not second
    assert len(fake_stanza) == 2


def test_processors_whitespace_normalized(fake_stanza):
    first = model_cache.get_stanza_pipeline(lang="en", processors="tokenize, lemma")
    second = model_cache.get_stanza_pipeline(lang="en", processors="tokenize,lemma")
    assert first is second
    assert len(fake_stanza) == 1
    assert fake_stanza[0]["processors"] == "tokenize,lemma"


def test_extra_kwargs_part_of_key(fake_stanza):
    first = model_cache.get_stanza_pipeline(lang="en", processors="tokenize", use_gpu=False)
    second = model_cache.get_stanza_pipeline(lang="en", processors="tokenize")
    assert first is not second
    assert len(fake_stanza) == 2


def test_spacy_disable_part_of_key(monkeypatch):
    calls = []
    monkeypatch.setitem(
        sys.modules,
        "spacy",
        types.SimpleNamespace(load=lambda name, disable: calls.append((name, tuple(disable))) or object()),
    )
    full = model_cache.get_spacy_model("en_core_web_sm")
    partial = model_cache.get_spacy_model("en_core_web_sm", disable=("parser", "ner"))
    again = model_cache.get_spacy_model("en_core_web_sm", disable=("parser", "ner"))
    assert full is not partial
    assert partial is again
    assert len(calls) == 2


def test_sentence_transformer_cached(monkeypatch):
    calls = []

    def ctor(name):
        calls.append(name)
        return object()

    monkeypatch.setitem(sys.modules, "sentence_transformers", types.SimpleNamespace(SentenceTransformer=ctor))
    first = model_cache.get_sentence_transformer()
    second = model_cache.get_sentence_transformer("all-MiniLM-L6-v2")
    assert first is second
    assert calls == ["all-MiniLM-L6-v2"]
