"""Tests for src/WSI_util.py.

Split from test_WSI.py (23 Nov 2026), whose docstring was:

Word sense induction (WSI_classes / WSI_util): the helpers that pick WHICH vector and WHICH k.

The keyword's vector used to be read one position too early: the model input starts with [CLS], the
wordpiece list does not, so position token_i held the PREVIOUS wordpiece. Senses were induced from the
word before the keyword. The k-means range also dropped its maximum, and a single keyword missing
from the corpus aborted the run.
"""

import sys
from unittest.mock import MagicMock

for _mod in (
    "sklearn",
    "sklearn.metrics",
    "sklearn.cluster",
    "sklearn.metrics.pairwise",
    "torch",
    "torch.nn",
    "transformers",
    "tqdm",
):
    sys.modules.setdefault(_mod, MagicMock())


import WSI_util  # noqa: E402


class TestParseKeywords:
    def test_comma_separated_lowercased(self):
        assert WSI_util.parse_keywords(" Bank, river ,BANK,, ") == ["bank", "river"]

    def test_csv_dictionary_file(self, tmp_path):
        # the "Select dictionary file" button puts the csv PATH into the keywords widget
        f = tmp_path / "words.csv"
        f.write_text("Bank,finance\nSpring\n\nbank\n", encoding="utf-8")
        assert WSI_util.parse_keywords(str(f)) == ["bank", "spring"]


class TestSplitFoundMissing:
    def test_splits_in_input_order(self):
        sents = [(0, "we sat on the bank", "a.txt"), (1, "spring came early", "b.txt")]
        assert WSI_util.split_found_missing(sents, ["spring", "gaze", "bank"]) == (["spring", "bank"], ["gaze"])

    def test_whole_words_only(self):
        sents = [(0, "the banker left", "a.txt")]
        assert WSI_util.split_found_missing(sents, ["bank"]) == ([], ["bank"])
