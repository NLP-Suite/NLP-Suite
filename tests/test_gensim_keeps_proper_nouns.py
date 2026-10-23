"""The Gensim topic model keeps proper nouns.

The texts are lowercased (gensim simple_preprocess) before spaCy tags them, and on lowercased text spaCy still tags
many names as proper nouns - first names, places, kin written as names - so a part-of-speech filter of noun, adjective,
verb and adverb dropped the people and places a corpus is about. The module is checked as text: it imports the heavy
libraries the tests stub."""

import os
import re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "topic_modeling_gensim_util.py")


def test_every_lemmatization_filter_keeps_proper_nouns():
    with open(SRC, encoding="utf-8-sig") as f:
        s = f.read()
    filters = re.findall(r"lemmatization\([^)]*allowed_postags=\[([^\]]*)\]", s, re.S)
    assert len(filters) >= 2
    assert all(re.search(r"[\"']PROPN[\"']", f) for f in filters)
