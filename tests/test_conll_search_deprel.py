"""Unit tests for the CoNLL table search's filters on the searched token (CoNLL_table_search_util)."""

import sys
from unittest.mock import MagicMock, patch

# imported at the top of CoNLL_table_search_util for the charts and network graphs, not used by the search itself
with patch.dict(sys.modules, {"Gephi_util": MagicMock()}):
    import CoNLL_table_search_util as search_util


def row(tid, form, pos, head, deprel):
    # ID, Form, Lemma, POS, NER, Head, DepRel, Deps, Clause Tag, Record ID, Sentence ID, Document ID, Document
    return [tid, form, form.lower(), pos, "O", head, deprel, f"{head}:{deprel}", "", tid, "1", "1", "doc.txt"]


# "They say we say ." -- 'say' is the ROOT once and a clausal complement (ccomp) once
SENTENCE = [
    row("1", "They", "PRP", "2", "nsubj"),
    row("2", "say", "VBP", "0", "ROOT"),
    row("3", "we", "PRP", "4", "nsubj"),
    row("4", "say", "VBP", "2", "ccomp"),
    row("5", ".", ".", "2", "punct"),
]


def searched_ids(deprel):
    found = search_util.search_in_sentence("say", SENTENCE, "LEMMA", "*", deprel)
    return sorted({keyword[0] for _, _, keyword in found})


def test_no_deprel_filter_returns_both():
    assert searched_ids("*") == ["2", "4"]


def test_deprel_filter_keeps_only_matching_searched_tokens():
    # the GUI's DEPREL filter for the searched token was passed in but never applied
    assert searched_ids("ROOT") == ["2"]
    assert searched_ids("ccomp") == ["4"]


def test_deprel_filter_with_no_match_returns_nothing():
    assert search_util.search_in_sentence("say", SENTENCE, "LEMMA", "*", "obj") == []


def test_co_occurring_tokens_of_the_kept_token_only():
    found = search_util.search_in_sentence("say", SENTENCE, "LEMMA", "*", "ccomp")
    # 'we' (its subject) and 'say' #2 (its governor) relate to the ccomp 'say'; 'They' belongs to the ROOT one
    assert sorted(str(related) for related, _, _ in found) == ["2", "3"]
