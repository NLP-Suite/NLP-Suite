"""Unit tests for the CoNLL table analyzer's verb tense and verb voice lists (CoNLL_verb_analysis_util)."""

import CoNLL_verb_analysis_util as verb_util


def row(record_id, form, pos, deprel="dep"):
    """One canonical CoNLL row: ID, Form, Lemma, POS, NER, Head, DepRel, Deps, Clause Tag, Record ID,
    Sentence ID, Document ID, Document, Date."""
    return [str(record_id), form, form.lower(), pos, "O", "0", deprel, "", "", str(record_id), "1", "1", "doc.txt", ""]


def table(*tokens):
    return [row(i + 1, form, pos, *rest) for i, (form, pos, *rest) in enumerate(tokens)]


def stats(rows):
    return dict(verb_util.verb_tense_data_preparation(rows)[1][1:])


def tense_column(rows):
    return {r[1]: r[-1] for r in verb_util.verb_tense_data_preparation(rows)[0]}


def test_will_marks_the_next_verb_future():
    # 'will' is tagged MD, which the tense loop skipped, so Future was always 0
    rows = table(("They", "PRP"), ("will", "MD"), ("go", "VB"), (".", "."))
    assert stats(rows)["Future"] == 1
    assert stats(rows)["Infinitive"] == 0
    assert tense_column(rows) == {"go": "Future"}


def test_capitalized_and_contracted_will():
    assert stats(table(("Will", "MD"), ("they", "PRP"), ("go", "VB")))["Future"] == 1
    assert stats(table(("They", "PRP"), ("'ll", "MD"), ("go", "VB")))["Future"] == 1
    assert stats(table(("They", "PRP"), ("wo", "MD"), ("n't", "RB"), ("go", "VB")))["Future"] == 1


def test_other_modals_do_not_make_future():
    rows = table(("They", "PRP"), ("can", "MD"), ("go", "VB"))
    assert stats(rows)["Future"] == 0
    assert stats(rows)["Infinitive"] == 1


def test_pending_will_does_not_reach_a_later_verb():
    # 'I will.' then 'They ran to leave.': 'leave' is an infinitive, and 'ran' still gets its row
    rows = table(
        ("I", "PRP"), ("will", "MD"), (".", "."), ("They", "PRP"), ("ran", "VBD"), ("to", "TO"), ("leave", "VB")
    )
    assert stats(rows)["Future"] == 0
    assert tense_column(rows) == {"ran": "Past", "leave": "Infinitive"}


def test_third_person_present_has_its_own_count():
    # VBZ was added to the non-3rd-person counter, so the 3rd-person row was always 0
    rows = table(("She", "PRP"), ("runs", "VBZ"), ("and", "CC"), ("they", "PRP"), ("walk", "VBP"))
    assert stats(rows)["Present (3rd person singular)"] == 1
    assert stats(rows)["Present (non-3rd person singular)"] == 1


def test_modals_get_no_tense_row():
    rows = table(("They", "PRP"), ("should", "MD"), ("go", "VB"))
    assert [r[1] for r in verb_util.verb_tense_data_preparation(rows)[0]] == ["go"]


def test_voice_leaves_the_table_rows_alone():
    rows = table(
        ("It", "PRP"),
        ("was", "VBD", "aux:pass"),
        ("eaten", "VBN"),
        ("and", "CC"),
        ("they", "PRP"),
        ("have", "VBP", "aux"),
        ("gone", "VBN"),
    )
    passive, active_aux, _, voice_stats = verb_util.verb_voice_compute_frequencies(rows)
    assert [r[1] for r in passive] == ["was eaten"]
    assert [r[1] for r in active_aux] == ["have gone"]
    # the voice lists used to write 'was eaten' into the CoNLL row itself, which the tense list then showed
    assert [r[1] for r in rows] == ["It", "was", "eaten", "and", "they", "have", "gone"]
    assert tense_column(rows)["eaten"] == "Past Principle/Passive"
