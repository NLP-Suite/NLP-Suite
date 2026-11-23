"""Tests for src/statistics_txt_util.py, one file per module (folded from 4 files, 23 Nov 2026).

From test_statistics_txt_util.py:

Proof-of-concept unit tests for the document-statistics helpers.

Targets the pure, stdlib-only functions in ``src/statistics_txt_util.py``. The
heavy GUI/NLP import machinery is neutralised by the stubs in ``conftest.py``;
if that ever stops working the import guard below skips the module rather than
erroring at collection time.

From test_sentence_complexity.py:

Unit tests for the sentence-complexity leaf count and per-sentence Yngve/Frazier scores.

conftest stubs ``tree`` and ``sentence_complexity_node_util`` (statistics_txt_util imports them at the top),
so the real, stdlib-only modules are loaded here from their files and swapped in where needed.

From test_spacytextblob_factory.py:

spaCy's TextBlob sentiment and Objectivity/subjectivity: the "spacytextblob" factory is registered (#1720).

spacytextblob registers the factory only when spacytextblob.spacytextblob is imported; without the import
nlp.add_pipe("spacytextblob") failed with E002 "Can't find factory".

From test_yule_k.py:

Unit tests for statistics_txt_util.yule_k_from_counts (Yule's K, Oakes 1998: 204).
"""

import pytest

try:
    import statistics_txt_util
    from statistics_txt_util import get_yules_k_i, tokenize, word_count
except (ImportError, SystemExit):  # pragma: no cover - defensive
    pytest.skip("statistics_txt_util dependencies not available", allow_module_level=True)


def test_word_count():
    assert word_count("the cat saw the dog") == {
        "the": 2,
        "cat": 1,
        "saw": 1,
        "dog": 1,
    }


def test_tokenize():
    assert tokenize("it's a fine-day today") == ["it's", "a", "fine-day", "today"]


def test_get_yules_k_i():
    # Needs repeated tokens: all-distinct tokens make m2 == m1 and divide by zero.
    k, i = get_yules_k_i("the cat and the dog and the bird")
    assert k > 0
    assert i > 0


class TestRepetitionK:
    """A blank, cancelled or non-numeric K used to end silently or crash (#1723)."""

    def test_a_number_is_used(self):
        assert statistics_txt_util.repetition_k("5", 4) == (5, "")

    def test_blank_falls_back_and_says_so(self):
        k, note = statistics_txt_util.repetition_k("", 4)
        assert k == 4 and "default K = 4" in note

    def test_cancel_returns_none(self):
        k, note = statistics_txt_util.repetition_k(None, 3)
        assert k == 3 and note

    def test_not_a_number(self):
        k, note = statistics_txt_util.repetition_k("three", 3)
        assert k == 3 and "'three'" in note

    def test_zero(self):
        k, note = statistics_txt_util.repetition_k("0", 4)
        assert k == 4 and note


# ---- formerly tests/test_sentence_complexity.py -------------------------------------------------------------

import importlib.util  # noqa: E402
import pathlib  # noqa: E402

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


# ---- formerly tests/test_spacytextblob_factory.py -----------------------------------------------------------

from unittest.mock import MagicMock, patch  # noqa: E402

import statistics_txt_util  # noqa: E402


def test_the_pipeline_imports_spacytextblob_before_add_pipe_and_loads_once():
    events = []
    nlp = MagicMock()
    nlp.add_pipe.side_effect = lambda name: events.append(("add_pipe", name))
    factory_module = MagicMock()

    real_import = __import__

    def tracking_import(name, *args, **kwargs):
        if name == "spacytextblob.spacytextblob":
            events.append(("import", name))
            return factory_module
        return real_import(name, *args, **kwargs)

    with (
        patch.object(statistics_txt_util, "_spacy_textblob_nlp", None),
        patch.object(statistics_txt_util.spacy, "load", return_value=nlp) as load,
        patch("builtins.__import__", side_effect=tracking_import),
    ):
        first = statistics_txt_util.spacy_textblob_pipeline()
        second = statistics_txt_util.spacy_textblob_pipeline()
    assert first is nlp and second is nlp
    assert load.call_count == 1
    assert events == [("import", "spacytextblob.spacytextblob"), ("add_pipe", "spacytextblob")]


def test_spacy_util_imports_the_factory_before_add_pipe():
    # spaCy_util is a large GUI-side module; check the source order instead of running spaCy_annotate
    import os

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "spaCy_util.py")
    src = open(path, encoding="utf-8").read()
    assert src.index("import spacytextblob.spacytextblob") < src.index('nlp.add_pipe("spacytextblob")')


# ---- formerly tests/test_yule_k.py --------------------------------------------------------------------------

try:
    from statistics_txt_util import yule_k_from_counts
except (ImportError, SystemExit):  # pragma: no cover - defensive
    pytest.skip("statistics_txt_util dependencies not available", allow_module_level=True)


def test_worked_example():
    # one type seen 3 times and four types seen 5 times: M1 = 23 tokens, M2 = 3^2 + 4 * 5^2 = 109
    assert yule_k_from_counts([3, 5, 5, 5, 5]) == round(10000 * (109 - 23) / (23 * 23), 2)


def test_every_word_distinct_is_zero():
    assert yule_k_from_counts([1, 1, 1, 1]) == 0


def test_lower_k_means_richer_vocabulary():
    varied = [2, 1, 1, 1, 1, 1, 1, 1]  # 9 tokens, 8 types
    repetitive = [5, 4]  # 9 tokens, 2 types
    assert yule_k_from_counts(varied) < yule_k_from_counts(repetitive)


def test_empty_text():
    assert yule_k_from_counts([]) == 0


def test_accepts_dict_values():
    assert yule_k_from_counts({"a": 2, "b": 1}.values()) == yule_k_from_counts([2, 1])
