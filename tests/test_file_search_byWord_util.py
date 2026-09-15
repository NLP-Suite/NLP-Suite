"""Unit test for where the word search writes its sentence extracts."""

import os

import pytest

try:
    from file_search_byWord_util import sentence_extract_filenames
except (ImportError, SystemExit):  # pragma: no cover - defensive
    pytest.skip("file_search_byWord_util dependencies not available", allow_module_level=True)


def test_extracts_land_inside_the_output_directory():
    out = os.path.join("NLP_output", "search_word_sent_corpus")
    with_words, without_words = sentence_extract_filenames(out)
    assert with_words == os.path.join(out, "NLP_extract_with_searchwords.txt")
    assert without_words == os.path.join(out, "NLP_extract_wo_searchwords.txt")
    assert os.path.dirname(with_words) == os.path.dirname(without_words) == out
