"""CoNLL Table Analyzer on a Stanza (or spaCy) table: token search finds the token, verb modals are found (#1765).

Search: CoNLL_table_search_util finds a token's related words only through the Deps (enhanced dependencies) column,
"3:obj" for a token whose head is 3. Stanford CoreNLP writes it; Stanza and spaCy do not, so normalize_to_canonical
left it empty and searching "book" reported nothing although "book" is a FORM in the table. With Deps empty the search
now uses Head (the same head:relation pair, unenhanced).

Modals: Stanza's table drops xpos and keeps Universal POS, where "would"/"can" are AUX; normalize_to_canonical
mapped AUX to VB*, never to MD, so the Verb Modals/Modality tables (which select POS == "MD") were empty. An AUX
whose lemma is an English modal now becomes MD, as CoreNLP tags it.

The table below is a small Stanza-format table (its columns in the order Stanza_util writes them).
"""

import sys
from unittest.mock import MagicMock, patch

import CoNLL_util

with patch.dict(sys.modules, {"Gephi_util": MagicMock()}):
    import CoNLL_table_search_util as search_util

STANZA_HEADER = [
    "ID", "Form", "Lemma", "POS", "NER", "feats", "Multi-Word Expression", "Head", "DepRel", "Clause Tag",
    "Record ID", "Sentence ID", "Document ID", "Document",
]  # fmt: skip
STANZA_ROWS = [
    ["1", "I", "I", "PRON", "O", "Case=Nom|Number=Sing|Person=1|PronType=Prs", "", "3", "nsubj", "", "1", "1", "1", "d"],
    ["2", "would", "would", "AUX", "O", "VerbForm=Fin", "", "3", "aux", "", "2", "1", "1", "d"],
    ["3", "read", "read", "VERB", "O", "VerbForm=Inf", "", "0", "root", "", "3", "1", "1", "d"],
    ["4", "the", "the", "DET", "O", "Definite=Def|PronType=Art", "", "5", "det", "", "4", "1", "1", "d"],
    ["5", "book", "book", "NOUN", "O", "Number=Sing", "", "3", "obj", "", "5", "1", "1", "d"],
    ["6", ".", ".", "PUNCT", "O", "", "", "3", "punct", "", "6", "1", "1", "d"],
    ["1", "The", "the", "DET", "O", "Definite=Def|PronType=Art", "", "2", "det", "", "7", "2", "1", "d"],
    ["2", "book", "book", "NOUN", "O", "Number=Sing", "", "4", "nsubj", "", "8", "2", "1", "d"],
    ["3", "can", "can", "AUX", "O", "VerbForm=Fin", "", "4", "aux", "", "9", "2", "1", "d"],
    ["4", "wait", "wait", "VERB", "O", "VerbForm=Inf", "", "0", "root", "", "10", "2", "1", "d"],
    ["5", "and", "and", "CCONJ", "O", "", "", "6", "cc", "", "11", "2", "1", "d"],
    ["6", "has", "have", "VERB", "O", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin", "", "4", "conj", "",
     "12", "2", "1", "d"],
]  # fmt: skip


def _normalized():
    return CoNLL_util.normalize_to_canonical(list(STANZA_HEADER), [list(r) for r in STANZA_ROWS])


def _sentences():
    _, data = _normalized()
    return [s for s in CoNLL_util.CoNLL_record_division(data) if s]


def test_searching_a_form_finds_its_related_words():
    first, second = _sentences()
    found_1 = search_util.search_in_sentence("book", first, "FORM")
    found_2 = search_util.search_in_sentence("book", second, "FORM")
    # sentence 1: "book" has head "read" (3) and dependent "the" (4); sentence 2: head "wait" (4), dependent "The" (1)
    assert sorted(str(related) for related, _, _ in found_1) == ["3", "4"]
    assert sorted(str(related) for related, _, _ in found_2) == ["1", "4"]
    assert {keyword[1] for _, _, keyword in found_1 + found_2} == {"book"}


def test_a_lemma_search_works_too():
    _, second = _sentences()
    found = search_util.search_in_sentence("have", second, "LEMMA")
    assert sorted(str(related) for related, _, _ in found) == ["4", "5"]  # "has": head "wait", dependent "and"


def test_modal_auxiliaries_become_MD():
    header, data = _normalized()
    pos = {row[header.index("Form")]: row[header.index("POS")] for row in data}
    assert pos["would"] == "MD"
    assert pos["can"] == "MD"
    assert pos["read"] == "VB" and pos["has"] == "VBZ"  # other verbs keep their Penn tags


def test_a_non_modal_auxiliary_is_not_MD():
    header = ["ID", "Form", "Lemma", "POS", "feats", "Head", "DepRel", "Sentence ID", "Document ID", "Document"]
    rows = [
        ["1", "is", "be", "AUX", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin", "0", "root", "1", "1", "d"]
    ]
    header, data = CoNLL_util.normalize_to_canonical(header, rows)
    assert data[0][header.index("POS")] == "VBZ"


def test_coreNLP_tables_are_unchanged():
    # Penn tags pass through; a CoreNLP table's Deps column is used as before (tests/test_conll_search_deprel.py)
    header = ["ID", "Form", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID",
              "Document ID", "Document"]  # fmt: skip
    rows = [["1", "would", "would", "MD", "O", "2", "aux", "2:aux", "", "1", "1", "1", "d"]]
    assert CoNLL_util.normalize_to_canonical(header, [list(r) for r in rows])[1] == rows
