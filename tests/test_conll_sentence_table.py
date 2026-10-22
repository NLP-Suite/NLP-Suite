"""Unit tests for the CoNLL table analyzer's 'Compute sentence table' (CoNLL_util.compute_sentence_table) and
the noun/verb lists of its Advanced analyses (CoNLL_util.get_nouns_verbs_CoNLL).

Both read the table with pandas, which conftest stubs, so the real pandas is swapped in for these tests (through
_real_pandas) and conftest's stub put back afterwards. Without pandas installed (as in CI) they are skipped.
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
