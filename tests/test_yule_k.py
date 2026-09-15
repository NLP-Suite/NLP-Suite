"""Unit tests for statistics_txt_util.yule_k_from_counts (Yule's K, Oakes 1998: 204)."""

import pytest

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
