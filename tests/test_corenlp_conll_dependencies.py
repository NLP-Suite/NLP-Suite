"""Unit tests for the Head / DepRel / Deps columns of the Stanford CoreNLP CoNLL table.

The fixture is CoreNLP 4.6.0 PCFG output (tokenize, ssplit, pos, lemma, ner, parse) for
"John and Mary left. She wanted to leave.", trimmed to the fields the parser routine reads. In both
sentences one token has two enhanced edges, so the enhanced graph cannot fill the one-edge Head/DepRel columns.
"""

import sys
from unittest.mock import MagicMock, patch

# Imported at the top of Stanford_CoreNLP_util but not needed by the json routines; CI installs only pytest.
_STUBS = [
    "pycorenlp",
    "Stanford_CoreNLP_clause_util",
    "Stanford_CoreNLP_SVO_enhanced_dependencies_util",
    "file_splitter_ByLength_util",
    "file_splitter_merged_txt_util",
    "parsers_annotators_visualization_util",
]
with patch.dict(sys.modules, {name: MagicMock() for name in _STUBS}):
    import Stanford_CoreNLP_util

# the PCFG parse trees are left out: these tests run the routine with pcfg=False (no clause tags)
JSON = {
    "sentences": [
        {
            "tokens": [
                {"index": 1, "word": "John", "lemma": "John", "pos": "NNP", "ner": "PERSON"},
                {"index": 2, "word": "and", "lemma": "and", "pos": "CC", "ner": "O"},
                {"index": 3, "word": "Mary", "lemma": "Mary", "pos": "NNP", "ner": "PERSON"},
                {"index": 4, "word": "left", "lemma": "leave", "pos": "VBD", "ner": "O"},
                {"index": 5, "word": ".", "lemma": ".", "pos": ".", "ner": "O"},
            ],
            "basicDependencies": [
                {"dep": "ROOT", "governor": 0, "dependent": 4},
                {"dep": "nsubj", "governor": 4, "dependent": 1},
                {"dep": "cc", "governor": 3, "dependent": 2},
                {"dep": "conj", "governor": 1, "dependent": 3},
                {"dep": "punct", "governor": 4, "dependent": 5},
            ],
            "enhancedDependencies": [
                {"dep": "ROOT", "governor": 0, "dependent": 4},
                {"dep": "nsubj", "governor": 4, "dependent": 1},
                {"dep": "cc", "governor": 3, "dependent": 2},
                {"dep": "conj:and", "governor": 1, "dependent": 3},
                {"dep": "nsubj", "governor": 4, "dependent": 3},
                {"dep": "punct", "governor": 4, "dependent": 5},
            ],
        },
        {
            "tokens": [
                {"index": 1, "word": "She", "lemma": "she", "pos": "PRP", "ner": "O"},
                {"index": 2, "word": "wanted", "lemma": "want", "pos": "VBD", "ner": "O"},
                {"index": 3, "word": "to", "lemma": "to", "pos": "TO", "ner": "O"},
                {"index": 4, "word": "leave", "lemma": "leave", "pos": "VB", "ner": "O"},
                {"index": 5, "word": ".", "lemma": ".", "pos": ".", "ner": "O"},
            ],
            "basicDependencies": [
                {"dep": "ROOT", "governor": 0, "dependent": 2},
                {"dep": "nsubj", "governor": 2, "dependent": 1},
                {"dep": "mark", "governor": 4, "dependent": 3},
                {"dep": "xcomp", "governor": 2, "dependent": 4},
                {"dep": "punct", "governor": 2, "dependent": 5},
            ],
            "enhancedDependencies": [
                {"dep": "ROOT", "governor": 0, "dependent": 2},
                {"dep": "nsubj", "governor": 2, "dependent": 1},
                {"dep": "nsubj:xsubj", "governor": 4, "dependent": 1},
                {"dep": "mark", "governor": 4, "dependent": 3},
                {"dep": "xcomp", "governor": 2, "dependent": 4},
                {"dep": "punct", "governor": 2, "dependent": 5},
            ],
        },
    ]
}


def _parser_rows():
    Stanford_CoreNLP_util.subtree_string = []  # a module global that CoreNLP_annotate sets up for each run
    rows, _, record_id = Stanford_CoreNLP_util.process_json_parser("", 1, "doc.txt", 0, 0, False, JSON)
    assert record_id == 10
    # columns: ID, Form, Lemma, POS, NER, Head, DepRel, Deps, Clause Tag, Record ID, Sentence ID, ...
    return {(row[10], row[1]): (row[5], row[6], row[7]) for row in rows}


def test_parser_conjunct_keeps_its_tree_edge():
    # Mary is a conjunct of John; the enhanced graph's propagated nsubj edge used to overwrite it
    assert _parser_rows()[("1", "Mary")] == (1, "conj", "1:conj:and|4:nsubj")


def test_parser_controlled_subject_attaches_to_the_main_verb():
    # She is the subject of 'wanted'; the enhanced nsubj:xsubj edge to 'leave' used to win
    assert _parser_rows()[("2", "She")] == (2, "nsubj", "2:nsubj|4:nsubj:xsubj")


def test_parser_tokens_with_one_edge_are_unchanged():
    rows = _parser_rows()
    assert rows[("1", "left")] == (0, "ROOT", "0:ROOT")
    assert rows[("2", "leave")] == (2, "xcomp", "2:xcomp")


def test_parser_head_and_deprel_form_one_tree_per_sentence():
    rows = _parser_rows()
    for sentence in ("1", "2"):
        deprels = [deprel for (sent, _), (_, deprel, _) in rows.items() if sent == sentence]
        assert deprels.count("ROOT") == 1
        assert not any(":" in d for d in deprels)  # no enhanced-only labels such as conj:and, nsubj:xsubj


def test_deprel_annotator_uses_the_tree():
    rows, record_id = Stanford_CoreNLP_util.process_json_deprel("", 1, "doc.txt", 0, 0, JSON)
    assert record_id == 10
    # columns: ID, Form, Head, DepRel, Record ID, Sentence ID, Document ID, Document
    by_form = {(row[5], row[1]): (row[2], row[3]) for row in rows}
    assert by_form[("1", "Mary")] == (1, "conj")
    assert by_form[("2", "She")] == (2, "nsubj")
