"""Proof-of-concept unit tests for the document-statistics helpers.

Targets the pure, stdlib-only functions in ``src/statistics_txt_util.py``. The
heavy GUI/NLP import machinery is neutralised by the stubs in ``conftest.py``;
if that ever stops working the import guard below skips the module rather than
erroring at collection time.
"""

import pytest

try:
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
