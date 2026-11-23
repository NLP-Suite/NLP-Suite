"""Tests for src/topic_modeling_gensim_util.py, one file per module (folded from 3 files, 23 Nov 2026).

From test_gensim_keeps_proper_nouns.py:

The Gensim topic model keeps proper nouns.

The texts are lowercased (gensim simple_preprocess) before spaCy tags them, and on lowercased text spaCy still tags
many names as proper nouns - first names, places, kin written as names - so a part-of-speech filter of noun, adjective,
verb and adverb dropped the people and places a corpus is about. The module is checked as text: it imports the heavy
libraries the tests stub.

From test_topic_corpus_size.py:

What the topic modeler says about corpus size.

It used to say "Topic modeling requires a large number of files (in the hundreds at least) to
produce valid results" and block, by default, under 50 files. Two faults. The number is not a
property of the method - a file is not a fixed quantity of text, and MALLET's own tutorial corpus is
under twenty documents. And it refused work the user had asked for on the strength of it.

What is true is narrower: per-document topic proportions are estimated per document, so with very
few documents the fitted topics are unstable across runs. The remedy is splitting long documents,
not reaching a file count.

From test_topic_document_topics.py:

Gensim topic modeling: the per-document topics csv.

A Gensim-only run wrote the pyLDAvis html and a topic-keywords csv but nothing per document, so there
was no way to see how the model categorized the corpus. Topics are reported 1-based, matching the
keywords csv and (with sort_topics=False) the pyLDAvis map.
"""

import os
import re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "topic_modeling_gensim_util.py")


def test_every_lemmatization_filter_keeps_proper_nouns():
    with open(SRC, encoding="utf-8-sig") as f:
        s = f.read()
    filters = re.findall(r"lemmatization\([^)]*allowed_postags=\[([^\]]*)\]", s, re.S)
    assert len(filters) >= 2
    assert all(re.search(r"[\"']PROPN[\"']", f) for f in filters)


# ---- formerly tests/test_topic_corpus_size.py ---------------------------------------------------------------

import importlib.util  # noqa: E402
import sys  # noqa: E402

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)

# corpus_size_advice is pure - it takes a number and returns two strings - but it lives in a module
# that imports the whole topic-modeling stack at import time. conftest stubs the top-level packages;
# `from gensim.utils import simple_preprocess` needs the DOTTED submodules stubbed too.
from unittest.mock import MagicMock  # noqa: E402

for _mod in (
    "gensim",
    "gensim.corpora",
    "gensim.utils",
    "gensim.models",
    "spacy",
    "pyLDAvis",
    "pyLDAvis.gensim",
    "pyLDAvis.gensim_models",
    "matplotlib",
    "matplotlib.pyplot",
    "pandas",
):
    sys.modules.setdefault(_mod, MagicMock())

_spec = importlib.util.spec_from_file_location("_real_topic_util", os.path.join(_SRC, "topic_modeling_gensim_util.py"))
tm = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(tm)
finally:
    os.chdir(_cwd)

advice = tm.corpus_size_advice


class TestWhenItRefuses:
    def test_no_documents_is_an_error(self):
        level, msg = advice(0)
        assert level == "error"
        assert "no .txt files" in msg

    def test_one_document_is_an_error_that_explains_why(self):
        """Not "you need hundreds" - the actual reason: there is nothing to compare it with."""
        level, msg = advice(1)
        assert level == "error"
        assert "ACROSS documents" in msg
        assert "split" in msg.lower()


class TestWhenItAdvises:
    def test_a_small_corpus_advises_but_does_NOT_refuse(self):
        level, msg = advice(20)
        assert level == "advice"
        assert "This will run" in msg

    def test_the_advice_names_the_real_risk(self):
        """Instability across runs, which is checkable - not an unsourced threshold."""
        msg = advice(20)[1]
        assert "shift from one run to the next" in msg
        assert "run it twice" in msg

    def test_it_does_not_claim_a_number_of_files_is_required(self):
        msg = advice(20)[1]
        low = msg.lower()
        assert "hundreds" not in low
        assert "requires a large number" not in low

    def test_it_says_what_actually_matters(self):
        msg = advice(20)[1]
        assert "amount of text" in msg
        assert "not the number of files" in msg

    def test_the_count_is_reported_back(self):
        assert "37" in advice(37)[1]


class TestWhenItSaysNothing:
    def test_a_large_corpus_gets_no_message(self):
        assert advice(200) == ("", "")

    def test_the_threshold_itself(self):
        assert advice(tm._FEW_DOCUMENTS)[0] == ""
        assert advice(tm._FEW_DOCUMENTS - 1)[0] == "advice"


class TestMalletsTutorialCorpus:
    def test_under_twenty_documents_runs_with_advice_not_a_refusal(self):
        """The case that started this: MALLET ships a tutorial corpus of fewer than 20 documents.
        The old dialog defaulted to No and would have stopped it."""
        level, _msg = advice(19)
        assert level == "advice"


# ---- formerly tests/test_topic_document_topics.py -----------------------------------------------------------

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)

# same loading as the corpus-size tests above: the module imports the whole topic-modeling stack at import time
for _mod in (
    "gensim",
    "gensim.corpora",
    "gensim.utils",
    "gensim.models",
    "spacy",
    "pyLDAvis",
    "pyLDAvis.gensim",
    "pyLDAvis.gensim_models",
    "matplotlib",
    "matplotlib.pyplot",
    "pandas",
):
    sys.modules.setdefault(_mod, MagicMock())

_spec_topic_document_topics = importlib.util.spec_from_file_location(
    "_real_topic_util_doc_topics", os.path.join(_SRC, "topic_modeling_gensim_util.py")
)
tm_topic_document_topics = importlib.util.module_from_spec(_spec_topic_document_topics)
_cwd = os.getcwd()
try:
    _spec_topic_document_topics.loader.exec_module(tm_topic_document_topics)
finally:
    os.chdir(_cwd)

KEYWORDS = {0: "cell, gene", 1: "say, know", 2: "metal, soil"}


def test_dominant_topic_is_one_based_with_its_keywords():
    rows = tm_topic_document_topics.document_topic_rows(["a.txt"], [[(0, 0.1), (1, 0.7), (2, 0.2)]], KEYWORDS)
    assert rows == [[1, "a.txt", 2, 0.7, "say, know"]]


def test_one_row_per_document_in_order():
    rows = tm_topic_document_topics.document_topic_rows(
        ["a.txt", "b.txt"], [[(2, 0.9), (0, 0.1)], [(0, 0.55), (1, 0.45)]], KEYWORDS
    )
    assert [(r[0], r[1], r[2]) for r in rows] == [(1, "a.txt", 3), (2, "b.txt", 1)]


def test_proportion_rounded():
    rows = tm_topic_document_topics.document_topic_rows(["a.txt"], [[(0, 0.123456789)]], KEYWORDS)
    assert rows[0][3] == 0.1235


def test_document_with_no_topics_is_kept_blank():
    assert tm_topic_document_topics.document_topic_rows(["empty.txt"], [[]], KEYWORDS) == [[1, "empty.txt", "", "", ""]]
