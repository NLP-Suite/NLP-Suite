"""Unit tests for the sentence-complexity leaf count and per-sentence Yngve/Frazier scores.

conftest stubs ``tree`` and ``sentence_complexity_node_util`` (statistics_txt_util imports them at the top),
so the real, stdlib-only modules are loaded here from their files and swapped in where needed.
"""

import importlib.util
import pathlib

import pytest

_SRC = pathlib.Path(__file__).resolve().parent.parent / "src"


def _load(name):
    spec = importlib.util.spec_from_file_location("real_" + name, _SRC / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tree = _load("tree")

# Stanza-style constituency parse: a single ROOT node, 6 leaves (the period counts as one)
PARSE = "(ROOT (S (NP (DT The) (NN dog)) (VP (VBD saw) (NP (DT the) (NN cat))) (. .)))"


def test_count_leaves_counts_every_leaf():
    assert tree.countLeaves(tree.make_tree(PARSE)) == 6


def test_count_leaves_single_leaf():
    assert tree.countLeaves(tree.make_tree("(NN dog)")) == 1


def test_nested_leaf_list_has_one_item_under_root():
    # why the scores equalled the sums: len() of this NESTED list is 1 for every ROOT-rooted parse
    assert len(tree.getLeavesAsList(tree.make_tree(PARSE))) == 1


@pytest.fixture
def scorer(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "tree", tree)
    node = _load("sentence_complexity_node_util")
    try:
        import statistics_txt_util
    except (ImportError, SystemExit):  # pragma: no cover - defensive
        pytest.skip("statistics_txt_util dependencies not available")
    monkeypatch.setattr(statistics_txt_util, "tree", tree)
    monkeypatch.setattr(statistics_txt_util, "Node", node)
    return statistics_txt_util.sentence_complexity_scores


def test_scores_are_sums_divided_by_leaves(scorer):
    y_avg, y_sum, f_avg, f_sum = scorer(PARSE)
    assert y_avg == round(y_sum / 6, 2)
    assert f_avg == round(f_sum / 6, 2)
    assert y_avg != y_sum
    assert f_avg != f_sum


def test_longer_sentence_same_shape_keeps_frazier_mean_close(scorer):
    # two conjoined copies of the same clause: the Frazier total grows with length, the mean barely moves
    short = scorer(PARSE)
    long_parse = (
        "(ROOT (S (S (NP (DT The) (NN dog)) (VP (VBD saw) (NP (DT the) (NN cat)))) (CC and)"
        " (S (NP (DT the) (NN cat)) (VP (VBD saw) (NP (DT the) (NN dog)))) (. .)))"
    )
    longer = scorer(long_parse)
    assert longer[3] > short[3]
    assert abs(longer[2] - short[2]) < short[2]
