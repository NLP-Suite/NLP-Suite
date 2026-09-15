"""Unit tests for the nominalization word-list lookup and the batched per-document detection.

Stanza, basic_NLP_util and CoNLL_util are replaced with fakes in sys.modules, and WordNet with a small
table, so the detection loop runs for real without any NLP library.
"""

from types import SimpleNamespace

import pytest

try:
    import nominalization_util
except (ImportError, SystemExit):  # pragma: no cover - defensive
    pytest.skip("nominalization_util dependencies not available", allow_module_level=True)

# noun -> base verb, standing in for WordNet derivational morphology
_BASE_VERBS = {"destruction": "destroy", "killing": "kill", "attack": "attack"}


def test_standard_ending_is_kept():
    assert nominalization_util.check_word_for_nominalization("destruction", set()) is False


def test_nonstandard_ending_is_skipped_unless_listed():
    assert nominalization_util.check_word_for_nominalization("attack", set()) is True
    assert nominalization_util.check_word_for_nominalization("attack", {"attack", "rape"}) is False


@pytest.fixture
def fake_nlp(monkeypatch):
    sentences = ["The destruction and the killing .", "Another destruction , a table ."]
    calls = []

    def basic_nlp_many(texts):
        calls.append(list(texts))
        # each token is a noun (NN) except punctuation and 'the'/'and'/'a'/'another'
        return [
            [(t, t, "DT" if t.lower() in {"the", "and", "a", "another"} else "NN") for t in s.split()] for s in texts
        ]

    monkeypatch.setitem(
        __import__("sys").modules,
        "Stanza_functions_util",
        SimpleNamespace(stanzaPipeLine=lambda text: text, sentence_split_stanza_text=lambda _doc: sentences),
    )
    monkeypatch.setitem(__import__("sys").modules, "basic_NLP_util", SimpleNamespace(basic_nlp_many=basic_nlp_many))
    monkeypatch.setitem(
        __import__("sys").modules, "CoNLL_util", SimpleNamespace(is_noun_POS=lambda pos: pos.startswith("NN"))
    )
    monkeypatch.setattr(nominalization_util, "_nominalization_base_verb", _BASE_VERBS.get)
    return calls


def test_detection_tags_all_sentences_in_one_call(fake_nlp):
    nominalization_util.nominalized_verb_detection(1, "doc.txt", "", "ignored", False, set())
    assert fake_nlp == [["The destruction and the killing .", "Another destruction , a table ."]]


def test_detection_counts(fake_nlp):
    nouns, by_sentence, noun_cnt, nominalized_cnt = nominalization_util.nominalized_verb_detection(
        1, "doc.txt", "", "ignored", False, set()
    )
    # first sighting of each nominalization is listed once, with its base verb
    assert [row[:2] for row in nouns] == [["destruction", "destroy"], ["killing", "kill"]]
    assert nominalized_cnt == {"destruction": 2, "killing": 1}
    # a noun that is not a nominalization is not counted on first sight, only on repeats (existing behavior)
    assert noun_cnt == {"destruction": 2, "killing": 1}
    # per sentence: words (every token except punctuation), nominalizations, count, percentage, sentence id
    assert [row[:5] for row in by_sentence] == [
        [5, "destruction; killing", 2, 40.0, 1],
        [4, "destruction", 1, 25.0, 2],
    ]


def test_detection_check_ending_uses_the_word_list(fake_nlp):
    nouns, _, _, _ = nominalization_util.nominalized_verb_detection(1, "doc.txt", "", "ignored", True, set())
    assert [row[0] for row in nouns] == ["destruction", "killing"]
