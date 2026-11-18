"""Proof-of-concept unit tests for the document-statistics helpers.

Targets the pure, stdlib-only functions in ``src/statistics_txt_util.py``. The
heavy GUI/NLP import machinery is neutralised by the stubs in ``conftest.py``;
if that ever stops working the import guard below skips the module rather than
erroring at collection time.
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
