"""Tests for src/CoNLL_util.py, one file per module (folded from 2 files, 23 Nov 2026).

From test_conll_sentence_table.py:

Unit tests for the CoNLL table analyzer's 'Compute sentence table' (CoNLL_util.compute_sentence_table) and
the noun/verb lists of its Advanced analyses (CoNLL_util.get_nouns_verbs_CoNLL).

Both read the table with pandas, which conftest stubs, so the real pandas is swapped in for these tests (through
_real_pandas) and conftest's stub put back afterwards. Without pandas installed (as in CI) they are skipped.

From test_conll_stanza_tables.py:

CoNLL Table Analyzer on a Stanza (or spaCy) table: token search finds the token, verb modals are found (#1765).

Search: CoNLL_table_search_util finds a token's related words only through the Deps (enhanced dependencies) column,
"3:obj" for a token whose head is 3. Stanford CoreNLP writes it; Stanza and spaCy do not, so normalize_to_canonical
left it empty and searching "book" reported nothing although "book" is a FORM in the table. With Deps empty the search
now uses Head (the same head:relation pair, unenhanced).

Modals: Stanza's table drops xpos and keeps Universal POS, where "would"/"can" are AUX; normalize_to_canonical
mapped AUX to VB*, never to MD, so the Verb Modals/Modality tables (which select POS == "MD") were empty. An AUX
whose lemma is an English modal now becomes MD, as CoreNLP tags it.

The table below is a small Stanza-format table (its columns in the order Stanza_util writes them).
"""

import csv

import _real_pandas
import pytest

import CoNLL_util

HEADER = [
    "ID",
    "Form",
    "Lemma",
    "POS",
    "NER",
    "Head",
    "DepRel",
    "Deps",
    "Clause Tag",
    "Record ID",
    "Sentence ID",
    "Document ID",
    "Document",
]

# doc 1: "The dog barked ." / "None came ." -- doc 2: "Cats sleep ."
TOKENS = [
    ("1", "The", "the", "DT", "det", "1", "1"),
    ("2", "dog", "dog", "NN", "nsubj", "1", "1"),
    ("3", "barked", "bark", "VBD", "ROOT", "1", "1"),
    ("4", ".", ".", ".", "punct", "1", "1"),
    ("1", "None", "none", "NN", "nsubj", "2", "1"),
    ("2", "came", "come", "VBD", "ROOT", "2", "1"),
    ("3", ".", ".", ".", "punct", "2", "1"),
    ("1", "Cats", "cat", "NNS", "nsubj", "1", "2"),
    ("2", "sleep", "sleep", "VBP", "ROOT", "1", "2"),
    ("3", ".", ".", ".", "punct", "1", "2"),
]


@pytest.fixture
def real_pandas(monkeypatch):
    # _real_pandas imports numpy/pandas once per run; importing them afresh here broke the next file to do so
    try:
        pandas, saved = _real_pandas.swap_in()
    except ImportError as exc:
        pytest.skip(f"real pandas not available: {exc}")
    monkeypatch.setattr(CoNLL_util, "pd", pandas)
    yield pandas
    _real_pandas.swap_out(saved)


@pytest.fixture
def conll(tmp_path):
    path = tmp_path / "parser" / "NLP_CoreNLP_PCFG_CoNLL.csv"
    path.parent.mkdir()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for record_id, (tid, form, lemma, pos, deprel, sent, doc) in enumerate(TOKENS, 1):
            writer.writerow([tid, form, lemma, pos, "O", "0", deprel, "", "", record_id, sent, doc, f"doc{doc}.txt"])
    return path


def sentence_rows(real_pandas, conll, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    written = CoNLL_util.compute_sentence_table(str(conll), str(out))
    return written, real_pandas.read_csv(written, keep_default_na=False).values.tolist()


def test_every_sentence_including_the_last(real_pandas, conll, tmp_path):
    _, rows = sentence_rows(real_pandas, conll, tmp_path)
    # columns: words, characters, Sentence ID, Sentence, Document ID, Document
    assert [(r[2], r[3], r[4]) for r in rows] == [
        (1, "The dog barked.", 1),
        (2, "None came.", 1),
        (1, "Cats sleep.", 2),  # the last sentence used to be dropped
    ]


def test_first_sentence_is_counted_like_the_others(real_pandas, conll, tmp_path):
    _, rows = sentence_rows(real_pandas, conll, tmp_path)
    # 'The dog barked.' is 3 words and 15 characters; a leading blank used to make it 4 and 16
    assert rows[0][:2] == [3, 15]
    assert rows[2][:2] == [2, 11]


def test_word_none_is_a_word(real_pandas, conll, tmp_path):
    # pandas read 'None' as a missing value, and a sentence starting with it crashed the loop
    _, rows = sentence_rows(real_pandas, conll, tmp_path)
    assert rows[1][3] == "None came."


def test_table_is_written_to_the_output_folder(real_pandas, conll, tmp_path):
    written, _ = sentence_rows(real_pandas, conll, tmp_path)
    # the input arrives as a full path, which made os.path.join drop the output folder
    assert written == str(tmp_path / "out" / "NLP_CoreNLP_PCFG_CoNLL_sentence.csv")


def test_noun_and_verb_lists(real_pandas, conll, tmp_path):
    files = CoNLL_util.get_nouns_verbs_CoNLL(str(conll), str(tmp_path))
    nouns_form, nouns_lemma, verbs_form, verbs_lemma = (
        sorted(real_pandas.read_csv(f).iloc[:, 0].astype(str)) for f in files
    )
    assert nouns_lemma == ["cat", "dog", "none"]
    assert verbs_form == ["barked", "came", "sleep"]
    assert verbs_lemma == ["bark", "come", "sleep"]


# ---- formerly tests/test_conll_stanza_tables.py -------------------------------------------------------------

import sys  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402

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
    # Penn tags pass through; a CoreNLP table's Deps column is used as before (tests/test_CoNLL_table_search_util.py)
    header = ["ID", "Form", "Lemma", "POS", "NER", "Head", "DepRel", "Deps", "Clause Tag", "Record ID", "Sentence ID",
              "Document ID", "Document"]  # fmt: skip
    rows = [["1", "would", "would", "MD", "O", "2", "aux", "2:aux", "", "1", "1", "1", "d"]]
    assert CoNLL_util.normalize_to_canonical(header, [list(r) for r in rows])[1] == rows


def test_heads_written_as_floats_are_followed():
    # Stanza_util writes Head through pandas as a float ("3.0", root "0.0"): the real table of the 5 sample reviews
    # has "14.0", and "14.0".isdigit() is False, so the search still found nothing on the zip
    rows = [r[:7] + [r[7] + ".0"] + r[8:] for r in STANZA_ROWS]
    _, data = CoNLL_util.normalize_to_canonical(list(STANZA_HEADER), rows)
    first, second = [s for s in CoNLL_util.CoNLL_record_division(data) if s]

    def related(sentence):
        return sorted(str(index) for index, _, _ in search_util.search_in_sentence("book", sentence, "FORM"))

    assert related(first) == ["3", "4"]
    assert related(second) == ["1", "4"]
