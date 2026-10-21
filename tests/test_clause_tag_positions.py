"""Unit tests for the PCFG clause tags written to the CoNLL table's Clause Tag column and to clausal_tags.csv.

conftest stubs nltk (CI installs only pytest), so the parse trees here are built with a minimal stand-in
for nltk.Tree: a list of children with a label(). That is all clausal_info_extract uses.
"""

import re

import Stanford_CoreNLP_clause_util as clause_util


class FakeTree(list):
    def __init__(self, label, children):
        super().__init__(children)
        self._label = label

    def label(self):
        return self._label


def tree(s):
    """Parse a bracketed tree like nltk.Tree.fromstring."""
    tokens = re.findall(r"\(|\)|[^\s()]+", s)
    pos = 0

    def node():
        nonlocal pos
        assert tokens[pos] == "("
        label = tokens[pos + 1]
        pos += 2
        children = []
        while tokens[pos] != ")":
            if tokens[pos] == "(":
                children.append(node())
            else:
                children.append(tokens[pos])
                pos += 1
        pos += 1
        return FakeTree(label, children)

    return node()


# "I saw a dog and a dog saw me ." -- the NP "a dog" occurs twice
REPEATED = tree(
    "(ROOT (S (S (NP (PRP I)) (VP (VBD saw) (NP (DT a) (NN dog)))) (CC and)"
    " (S (NP (DT a) (NN dog)) (VP (VBD saw) (NP (PRP me)))) (. .)))"
)


def test_constituent_spans_are_positions_in_preorder():
    spans, leaves = clause_util.constituent_spans(tree("(S (NP (DT the) (NN cat)) (VP (VBD sat)))"))
    assert leaves == ["the", "cat", "sat"]
    assert [(t.label(), start, end) for t, start, end in spans] == [
        ("S", 0, 2),
        ("NP", 0, 1),
        ("DT", 0, 0),
        ("NN", 1, 1),
        ("VP", 2, 2),
        ("VBD", 2, 2),
    ]


def test_repeated_phrase_gets_its_own_span():
    full_list, clausal_tags = clause_util.clausal_info_extract(REPEATED)
    noun_phrases = [(example, span) for label, example, span in clausal_tags if label == "NP"]
    # the second "a dog" used to be reported at tokens 2-3, where the first one is
    assert ("a dog", (2, 3)) in noun_phrases
    assert ("a dog", (5, 6)) in noun_phrases


def test_repeated_phrase_tags_the_right_token():
    full_list, _ = clause_util.clausal_info_extract(REPEATED)
    # token 5 ('a') starts the second clause's subject NP; it used to be tagged S, and the NP tag landed on token 2
    assert full_list[5] == ["NP"]
    assert full_list[2] == ["NP"]


def test_innermost_constituent_starting_at_a_token_wins():
    full_list, _ = clause_util.clausal_info_extract(REPEATED)
    # S, S, NP and PRP all start at token 0; the last one visited (PRP) is the tag, as before
    assert full_list[0] == ["PRP"]
    assert len(full_list) == 10


def test_example_string_is_cleaned_as_before():
    _, clausal_tags = clause_util.clausal_info_extract(REPEATED)
    assert clausal_tags[0] == ("S", "I saw a dog and a dog saw me.", (0, 9))


def test_clause_analysis_runs_without_clausal_tags_csv(tmp_path):
    # a CoNLL table moved out of its parser folder, or made by Stanza: no clausal_tags.csv and no Json beside it
    import CoNLL_clause_analysis_util

    table = tmp_path / "NLP_CoreNLP_PCFG_CoNLL.csv"
    table.write_text("ID,Form\n")
    assert CoNLL_clause_analysis_util.process_Json(str(table), str(tmp_path)) is None


def test_existing_clausal_tags_csv_is_still_returned(tmp_path):
    import CoNLL_clause_analysis_util

    table = tmp_path / "NLP_CoreNLP_PCFG_CoNLL.csv"
    table.write_text("ID,Form\n")
    (tmp_path / "clausal_tags.csv").write_text("Clause tag\n")
    assert CoNLL_clause_analysis_util.process_Json(str(table), str(tmp_path)) == str(tmp_path / "clausal_tags.csv")


def _json_folder(tmp_path, monkeypatch, *objects):
    """A CoNLL table with a CoreNLP Json_ folder beside it but no clausal_tags.csv. IO_files_util and IO_csv_util
    are conftest stubs, so the folder listing and the csv writer are replaced with real stand-ins."""
    import json

    import CoNLL_clause_analysis_util

    table = tmp_path / "NLP_CoreNLP_PCFG_CoNLL.csv"
    table.write_text("ID,Form\n")
    json_dir = tmp_path / "Json_corpus"
    json_dir.mkdir()
    json_file = json_dir / "Json_doc1_PCFG.txt"
    # exportJson appends, so one file can hold several objects back to back
    json_file.write_text("".join(json.dumps(o, indent=4) for o in objects), encoding="utf-8")
    written = {}

    def list_to_csv(window, rows, filename, colnum=0, encoding="utf-8"):
        written["rows"], written["filename"], written["encoding"] = rows, filename, encoding

    monkeypatch.setattr(CoNLL_clause_analysis_util.IO_files_util, "getFileList", lambda *a, **k: [str(json_file)])
    monkeypatch.setattr(CoNLL_clause_analysis_util.IO_csv_util, "list_to_csv", list_to_csv)
    monkeypatch.setattr(clause_util, "clausal_info_extract_from_string", lambda s: (["full " + s], ("S", s, (0, 1))))
    return CoNLL_clause_analysis_util, table, written


def test_clausal_tags_csv_is_rebuilt_from_the_Json_folder(tmp_path, monkeypatch):
    # a Json_ folder beside the table: the file text was indexed as JSON (TypeError) and the csv was written
    # with an undefined language_encoding (NameError), so this branch never ran
    first = {"sentences": [{"parse": "(ROOT (S a))"}]}
    second = {"sentences": [{"parse": "(ROOT (S b))"}, {"basicDependencies": []}]}  # 2nd sentence: no tree
    module, table, written = _json_folder(tmp_path, monkeypatch, first, second)
    result = module.process_Json(str(table), str(tmp_path))
    assert result == str(tmp_path / "clausal_tags.csv")
    assert written["filename"] == result
    assert written["encoding"] == "utf-8"
    assert [row[1] for row in written["rows"]] == ["(ROOT (S a))", "(ROOT (S b))"]


def test_Json_folder_without_parse_trees_writes_nothing(tmp_path, monkeypatch):
    # nn parser output has no constituency tree: no csv, and no path to a file that does not exist
    module, table, written = _json_folder(tmp_path, monkeypatch, {"sentences": [{"basicDependencies": []}]})
    assert module.process_Json(str(table), str(tmp_path)) is None
    assert written == {}
