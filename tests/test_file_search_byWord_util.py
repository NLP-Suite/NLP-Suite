"""Tests for src/file_search_byWord_util.py, one file per module (folded from 2 files, 23 Nov 2026).

From test_file_search_byWord_util.py:

Unit test for where the word search writes its sentence extracts.

From test_search_sentences_documents_calls.py:

Every call to file_search_byWord_util.search_sentences_documents passes the arguments it requires (#1761).

"Sample corpus by keywords in documents" (sample_corpus_main.run) called it without minus_K_var, plus_K_var and
extract_sentences, which the function requires: TypeError, so no subcorpus could be made from words in the documents.
The test binds each call in src/ (positional and keyword arguments, read with ast) to the function's signature.
"""

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


# ---- formerly tests/test_search_sentences_documents_calls.py ------------------------------------------------

import ast  # noqa: E402
import glob  # noqa: E402
import inspect  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _signature():
    source = open(os.path.join(SRC, "file_search_byWord_util.py"), encoding="utf-8-sig").read()
    node = next(
        n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "search_sentences_documents"
    )
    node.body = [ast.Pass()]
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), "f", "exec"), namespace)
    return inspect.signature(namespace["search_sentences_documents"])


def _calls():
    for path in sorted(glob.glob(os.path.join(SRC, "*.py"))):
        tree = ast.parse(open(path, encoding="utf-8-sig").read())
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "search_sentences_documents":
                yield pytest.param(n, id=f"{os.path.basename(path)}:{n.lineno}")


@pytest.mark.parametrize("call", list(_calls()))
def test_call_binds_to_the_signature(call):
    _signature().bind(*range(len(call.args)), **{k.arg: None for k in call.keywords})


def test_sample_corpus_calls_it():
    assert any("sample_corpus_main" in p.id for p in _calls())
