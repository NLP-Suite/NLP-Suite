"""Gensim topic modeling: the per-document topics csv.

A Gensim-only run wrote the pyLDAvis html and a topic-keywords csv but nothing per document, so there
was no way to see how the model categorized the corpus. Topics are reported 1-based, matching the
keywords csv and (with sort_topics=False) the pyLDAvis map.
"""

import importlib.util
import os
import sys
from unittest.mock import MagicMock

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)

# same loading as test_topic_corpus_size: the module imports the whole topic-modeling stack at import time
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

_spec = importlib.util.spec_from_file_location(
    "_real_topic_util_doc_topics", os.path.join(_SRC, "topic_modeling_gensim_util.py")
)
tm = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(tm)
finally:
    os.chdir(_cwd)

KEYWORDS = {0: "cell, gene", 1: "say, know", 2: "metal, soil"}


def test_dominant_topic_is_one_based_with_its_keywords():
    rows = tm.document_topic_rows(["a.txt"], [[(0, 0.1), (1, 0.7), (2, 0.2)]], KEYWORDS)
    assert rows == [[1, "a.txt", 2, 0.7, "say, know"]]


def test_one_row_per_document_in_order():
    rows = tm.document_topic_rows(["a.txt", "b.txt"], [[(2, 0.9), (0, 0.1)], [(0, 0.55), (1, 0.45)]], KEYWORDS)
    assert [(r[0], r[1], r[2]) for r in rows] == [(1, "a.txt", 3), (2, "b.txt", 1)]


def test_proportion_rounded():
    rows = tm.document_topic_rows(["a.txt"], [[(0, 0.123456789)]], KEYWORDS)
    assert rows[0][3] == 0.1235


def test_document_with_no_topics_is_kept_blank():
    assert tm.document_topic_rows(["empty.txt"], [[]], KEYWORDS) == [[1, "empty.txt", "", "", ""]]
