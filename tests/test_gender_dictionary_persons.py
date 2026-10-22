"""Gender dictionary annotator: only words CoreNLP NER tags as PERSON are looked up in the name list.

The name lists contain common words ('In', 'My', 'Will', 'May'), so matched against every word of a text they tag
prepositions and modals as male or female. ``NER_person_words`` and ``write_person_dictionary`` restrict the list to
the names NER actually found; ``dictionary_of_NER_persons`` (which runs CoreNLP) only glues them together.
"""

import csv
import sys
from unittest.mock import MagicMock, patch

import pytest

with patch.dict(sys.modules, {"Stanford_CoreNLP_util": MagicMock()}):
    try:
        from html_annotator_gender_dictionary_util import NER_person_words, write_person_dictionary
    except (ImportError, SystemExit):  # pragma: no cover - defensive
        pytest.skip("html_annotator_gender_dictionary_util dependencies not available", allow_module_level=True)


def test_only_PERSON_words_are_kept_and_split():
    rows = [("Iain Frame", "PERSON"), ("Diabetes UK", "ORGANIZATION"), ("Sally", "PERSON"), ("France", "COUNTRY")]
    assert NER_person_words(rows) == {"iain", "frame", "sally"}


def test_pronouns_tagged_PERSON_are_not_names():
    rows = [("She", "PERSON"), ("his", "PERSON"), ("Ann", "PERSON")]
    assert NER_person_words(rows) == {"ann"}


def test_no_PERSON_gives_no_words():
    assert NER_person_words([("Monday", "DATE")]) == set()


def _write(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def _read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_dictionary_keeps_only_names_found_by_NER(tmp_path):
    # the 1990 Census list has 'In', 'My' and 'May' as women's names
    src = tmp_path / "Census.csv"
    _write(
        src,
        ["Name", "Frequecy_in_percent", "Gender"],
        [["Sally", "0.1", "Female"], ["In", "0.001", "Female"], ["My", "0.001", "Female"], ["Iain", "0.01", "Male"]],
    )
    out = tmp_path / "persons.csv"
    kept = write_person_dictionary(str(src), "Name", {"sally", "iain", "frame"}, str(out))
    assert kept == 2
    assert [r["Name"] for r in _read(out)] == ["Sally", "Iain"]
    assert list(_read(out)[0]) == ["Name", "Frequecy_in_percent", "Gender"]  # header and columns unchanged


def test_dictionary_name_column_and_case(tmp_path):
    # the Carnegie Mellon list calls its column 'Names'; the US Social Security list repeats a name by year
    src = tmp_path / "CMU.csv"
    _write(src, ["Names", "Gender"], [["Will", "Male"], ["JOHN", "Male"], ["John", "Male"]])
    out = tmp_path / "persons.csv"
    assert write_person_dictionary(str(src), "Names", {"john"}, str(out)) == 2
    assert [r["Names"] for r in _read(out)] == ["JOHN", "John"]
