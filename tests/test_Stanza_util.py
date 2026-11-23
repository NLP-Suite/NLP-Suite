"""Stanza_annotate lists each output csv once, not once per document.

Its loop over the input documents appended the run's one output csv (and the SVO and location csvs) on every
document, and the charts loop after it charts every csv in that list: on 958 documents the lemma table was charted
958 times, about 38 s each (10 hours), and the sentiment table 958 times (about 43 minutes).
"""

import ast
import os
import types

import pytest

_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "Stanza_util.py")


@pytest.fixture(scope="module")
def stanza_util():
    # Only add_output_file, compiled from the source: importing Stanza_util pulls in a module that builds a Tk window,
    # which fails on CI (no display).
    tree = ast.parse(open(_PATH, encoding="utf-8").read())
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "add_output_file")
    namespace = {}
    exec(compile(ast.Module(body=[func], type_ignores=[]), _PATH, "exec"), namespace)
    return types.SimpleNamespace(add_output_file=namespace["add_output_file"])


def test_each_file_is_added_once_in_first_seen_order(stanza_util):
    files = []
    for _ in range(958):  # one call per document, as in the loop
        stanza_util.add_output_file(files, "NLP_CoNLL_Stanza.csv")
        stanza_util.add_output_file(files, "NLP_SVO_Stanza.csv")
    # SVO_main reads [0] as the CoNLL table and [1] as the SVO table
    assert files == ["NLP_CoNLL_Stanza.csv", "NLP_SVO_Stanza.csv"]


def test_the_document_loop_does_not_append_directly():
    tree = ast.parse(open(_PATH, encoding="utf-8").read())
    annotate = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "Stanza_annotate")
    doc_loop = next(
        n for n in ast.walk(annotate) if isinstance(n, ast.For) and getattr(n.iter, "id", "") == "inputDocs"
    )
    direct = [
        ast.unparse(n)
        for n in ast.walk(doc_loop)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "append"
        and getattr(n.func.value, "id", "") == "filesToOpen"
    ]
    assert direct == []
