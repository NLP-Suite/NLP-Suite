"""ANEW, hedonometer, SentiWordNet and VADER lemmatize each word with its own Stanza pipeline run.

lemmatize_stanza_word_cached gives the same lemma as lemmatize_stanza_word(stanzaPipeLine(word)) and runs the pipeline
once per distinct word, not once per occurrence.
"""

import importlib.util
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
_PATH = os.path.join(_SRC, "Stanza_functions_util.py")


@pytest.fixture
def sfu():
    stubs = {
        name: MagicMock() for name in ("stanza",) if name not in sys.modules or isinstance(sys.modules[name], MagicMock)
    }
    with patch.dict(sys.modules, stubs):
        spec = importlib.util.spec_from_file_location("_sfu_lemma_cache", _PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    yield module


def _fake_pipeline(word):
    lemma = {"went": "go", "dogs": "dog"}.get(word, word)
    return SimpleNamespace(sentences=[SimpleNamespace(words=[SimpleNamespace(lemma=lemma, text=word)])])


def test_same_lemmas_one_pipeline_run_per_distinct_word(sfu):
    pipeline = MagicMock(side_effect=_fake_pipeline)
    words = ["went", "dogs", "went", "happy", "dogs", "went"]
    with patch.object(sfu, "stanzaPipeLine", pipeline):
        cached = [sfu.lemmatize_stanza_word_cached(w) for w in words]
    expected = ["go", "dog", "go", "happy", "dog", "go"]
    assert cached == [sfu.lemmatize_stanza_word(_fake_pipeline(w)) for w in words] == expected
    assert pipeline.call_count == 3


@pytest.mark.parametrize("tool", ["ANEW", "hedonometer", "SentiWordNet", "VADER"])
def test_sentiment_dictionaries_use_the_cached_lemma(tool):
    source = open(os.path.join(_SRC, f"sentiment_analysis_{tool}_util.py"), encoding="utf-8").read()
    assert "lemmatize_stanza_word(stanzaPipeLine(" not in source
    assert "lemmatize_stanza_word_cached(" in source
