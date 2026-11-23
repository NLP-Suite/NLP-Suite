"""File splitter, "Split by word(s) (extract sentences)": sentence_analysis_util.extract_sentences exists again (#1760).

file_splitter_main.run called sentence_analysis_util.extract_sentences, which no longer existed: AttributeError. It is
back, doing what the GUI's help says: for each input file, NLP_<file>_extract.txt with the sentences that contain one
of the search words and NLP_<file>_extract_wo-searchword.txt with the others. Stanza (the sentence splitter, as in
Word search) is stubbed with a splitter on ". ".
"""

import ast
import inspect
import os
import sys
from unittest.mock import MagicMock

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


@pytest.fixture
def sentence_analysis_util(monkeypatch):
    stanza_functions = MagicMock()
    stanza_functions.stanzaPipeLine.side_effect = lambda text: text
    stanza_functions.sentence_split_stanza_text.side_effect = lambda text: [
        s if s.endswith(".") else s + "." for s in text.strip().split(". ") if s
    ]
    monkeypatch.setitem(sys.modules, "Stanza_functions_util", stanza_functions)
    import sentence_analysis_util

    return sentence_analysis_util


def test_sentences_are_split_by_whether_they_contain_a_search_word(sentence_analysis_util):
    sentences = ["I read the book.", "Bookish people.", "She loves coming out.", "Nothing here."]
    found, not_found = sentence_analysis_util.sentences_with_and_without_words(sentences, "book, coming out")
    assert found == ["I read the book.", "She loves coming out."]
    assert not_found == ["Bookish people.", "Nothing here."]


def test_extract_sentences_writes_both_files_for_each_input_file(sentence_analysis_util, tmp_path, monkeypatch):
    doc = tmp_path / "review.txt"
    doc.write_text("I read the book. It rained. The book was long.", encoding="utf-8")
    monkeypatch.setattr(sentence_analysis_util.IO_files_util, "getFileList", MagicMock(return_value=[str(doc)]))
    out = tmp_path / "out"
    out.mkdir()
    files = sentence_analysis_util.extract_sentences(
        MagicMock(), str(doc), "", str(out), "book", "NLP_default_IO_config.csv"
    )
    with_words = out / "NLP_review_extract.txt"
    without = out / "NLP_review_extract_wo-searchword.txt"
    assert files == [str(with_words), str(without)]
    assert with_words.read_text(encoding="utf-8").splitlines() == ["I read the book.", "The book was long."]
    assert without.read_text(encoding="utf-8").splitlines() == ["It rained."]


def test_file_splitter_calls_extract_sentences_as_it_is_defined(sentence_analysis_util):
    source = open(os.path.join(SRC, "file_splitter_main.py"), encoding="utf-8").read()
    calls = [
        n
        for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "extract_sentences"
    ]
    assert len(calls) == 1
    inspect.signature(sentence_analysis_util.extract_sentences).bind(*range(len(calls[0].args)))
