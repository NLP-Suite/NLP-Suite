"""Word sense induction (WSI_classes / WSI_util): the helpers that pick WHICH vector and WHICH k.

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

import WSI_classes  # noqa: E402
import WSI_util  # noqa: E402


def _fake_layers(n_layers=12, n_sents=2, n_positions=6):
    """encoded_layers[layer][sent][pos] == (layer, sent, pos), so a lookup shows where it read."""
    return [
        [[(layer, sent, pos) for pos in range(n_positions)] for sent in range(n_sents)] for layer in range(n_layers)
    ]


class TestLastFourLayers:
    def test_reads_the_position_after_cls(self):
        # wordpieces ['the', 'bank'] are fed as [CLS] the bank [SEP]: 'bank' (token_i=1) is position 2
        got = WSI_classes.last_four_layers(_fake_layers(), sent_i=1, token_i=1)
        assert [pos for _, _, pos in got] == [2, 2, 2, 2]

    def test_first_wordpiece_is_not_cls(self):
        got = WSI_classes.last_four_layers(_fake_layers(), sent_i=0, token_i=0)
        assert all(pos == 1 for _, _, pos in got)

    def test_last_four_layers_newest_first(self):
        got = WSI_classes.last_four_layers(_fake_layers(n_layers=13), sent_i=0, token_i=0)
        assert [layer for layer, _, _ in got] == [12, 11, 10, 9]


class TestCandidateKs:
    def test_maximum_is_included(self):
        # GUI sliders read MIN 4, MAX 6: all three are tried (it used to be 4 and 5)
        assert WSI_classes.candidate_ks((4, 6), n_samples=100) == [4, 5, 6]

    def test_capped_by_occurrences(self):
        # silhouette needs k <= n_samples - 1
        assert WSI_classes.candidate_ks((2, 6), n_samples=4) == [2, 3]

    def test_never_below_two(self):
        assert WSI_classes.candidate_ks((1, 3), n_samples=100) == [2, 3]

    def test_too_few_occurrences_gives_nothing(self):
        assert WSI_classes.candidate_ks((4, 6), n_samples=3) == []


class TestBestK:
    def test_highest_score(self):
        assert WSI_classes.best_k({2: 0.1, 3: 0.4, 4: 0.2}) == 3

    def test_negative_scores(self):
        assert WSI_classes.best_k({2: -0.3, 3: -0.1}) == 3

    def test_tie_goes_to_fewer_senses(self):
        assert WSI_classes.best_k({4: 0.5, 2: 0.5}) == 2


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
