"""SVO '*' (all parsers): each parser pair's comparison files get their own names.

With one fixed name per kind, the three pairs overwrote each other in the same output folder and only CoreNLP vs
Stanza was left (found while checking the HW 4 tools).
"""

import SVO_compare_util


def test_each_pair_has_its_own_file_names():
    pairs = ["spaCy_vs_CoreNLP", "spaCy_vs_Stanza", "CoreNLP_vs_Stanza"]
    for kind in ("summary", "differences", "shared"):
        names = {SVO_compare_util.comparison_label(kind, pair) for pair in pairs}
        assert len(names) == 3


def test_a_single_comparison_keeps_the_old_name():
    assert SVO_compare_util.comparison_label("summary") == "SVO_comparison_summary"
