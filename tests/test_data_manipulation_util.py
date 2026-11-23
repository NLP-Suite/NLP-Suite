"""Tests for src/data_manipulation_util.py, one file per module (folded from 2 files, 23 Nov 2026).

From test_data_manipulation_util.py:

Tests for distinct_values, which fills the WHERE clause pick-list.

From test_evan_regressions.py:

Regressions for the three bugs Evan found testing v1.6.30 on Mac and Windows.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import data_manipulation_util as dm  # noqa: E402


def write_csv(tmp_path, text, name="corpus.csv"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


CSV = (
    "Newspaper,Year,Note\n"
    "The Atlanta Constitution,1892,first\n"
    "The Macon Telegraph,1893,second\n"
    "The Atlanta Constitution,1892,third\n"
    "The Savannah Tribune,1918,\n"
)


class TestDistinctValues:
    def test_returns_distinct_sorted_strings(self, tmp_path):
        got = dm.distinct_values(write_csv(tmp_path, CSV), "Newspaper")
        assert got == ["The Atlanta Constitution", "The Macon Telegraph", "The Savannah Tribune"]

    def test_duplicates_collapse(self, tmp_path):
        # 'The Atlanta Constitution' appears twice in the file
        assert len(dm.distinct_values(write_csv(tmp_path, CSV), "Newspaper")) == 3

    def test_numeric_column_sorts_numerically(self, tmp_path):
        got = dm.distinct_values(write_csv(tmp_path, CSV), "Year")
        assert got == ["1892", "1893", "1918"]

    def test_numeric_sort_is_not_lexicographic(self, tmp_path):
        csv = "Year\n9\n1892\n100\n"
        assert dm.distinct_values(write_csv(tmp_path, csv), "Year") == ["9", "100", "1892"]

    def test_blank_and_missing_values_are_dropped(self, tmp_path):
        got = dm.distinct_values(write_csv(tmp_path, CSV), "Note")
        assert got == ["first", "second", "third"]  # the empty Note is not offered

    def test_limit_caps_the_list(self, tmp_path):
        csv = "W\n" + "\n".join("w%d" % i for i in range(50))
        assert len(dm.distinct_values(write_csv(tmp_path, csv), "W", limit=10)) == 10

    def test_missing_column_returns_empty(self, tmp_path):
        assert dm.distinct_values(write_csv(tmp_path, CSV), "NoSuchColumn") == []

    def test_missing_file_returns_empty(self, tmp_path):
        assert dm.distinct_values(str(tmp_path / "nope.csv"), "Newspaper") == []

    def test_empty_arguments_return_empty(self, tmp_path):
        assert dm.distinct_values("", "Newspaper") == []
        assert dm.distinct_values(write_csv(tmp_path, CSV), "") == []

    def test_unreadable_file_returns_empty_rather_than_raising(self, tmp_path):
        # a convenience list must never take the GUI down
        p = tmp_path / "broken.csv"
        p.write_bytes(b"\xff\xfe\x00 not a csv at all \x00\xff")
        assert dm.distinct_values(str(p), "Newspaper") == []

    def test_values_are_stripped(self, tmp_path):
        csv = "City\n  Atlanta  \nMacon\n"
        assert dm.distinct_values(write_csv(tmp_path, csv), "City") == ["Atlanta", "Macon"]

    def test_case_variants_are_kept_separate(self, tmp_path):
        # the WHERE clause is case-sensitive, so both spellings must be offerable
        csv = "Name\nCOBB\nCobb\n"
        assert dm.distinct_values(write_csv(tmp_path, csv), "Name") == ["COBB", "Cobb"]


# ---- formerly tests/test_evan_regressions.py ----------------------------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))


class _Recorder:
    def __init__(self):
        self.warnings = []

    def showwarning(self, title, message):
        self.warnings.append((title, message))


class TestAppendEmptyField:
    """APPEND raised KeyError: '' when a listed file had no field selected."""

    def test_empty_field_is_rejected_with_a_message(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(dm, "mb", rec)
        assert dm.check_fields_selected(["Year", ""], "APPEND") is False
        assert len(rec.warnings) == 1
        title, message = rec.warnings[0]
        assert "APPEND" in message
        assert "field" in message.lower()

    def test_whitespace_only_field_is_rejected(self, monkeypatch):
        monkeypatch.setattr(dm, "mb", _Recorder())
        assert dm.check_fields_selected(["Year", "   "], "APPEND") is False

    def test_all_fields_present_passes_silently(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(dm, "mb", rec)
        assert dm.check_fields_selected(["Year", "City"], "APPEND") is True
        assert rec.warnings == []

    def test_a_single_record_is_handled(self, monkeypatch):
        monkeypatch.setattr(dm, "mb", _Recorder())
        assert dm.check_fields_selected([""], "APPEND") is False
        assert dm.check_fields_selected(["Year"], "APPEND") is True

    def test_append_returns_empty_instead_of_raising(self, monkeypatch):
        # the record shape the GUI builds when no field was picked: 'path,'
        monkeypatch.setattr(dm, "mb", _Recorder())
        assert dm.append("/tmp", ["C:/corpus/data.csv,"]) == ""

    def test_concatenate_is_guarded_too(self, monkeypatch):
        monkeypatch.setattr(dm, "mb", _Recorder())
        assert dm.concatenate("/tmp", ["C:/corpus/data.csv,", "C:/corpus/other.csv,"]) == ""

    def test_non_string_headers_do_not_crash_the_check(self, monkeypatch):
        monkeypatch.setattr(dm, "mb", _Recorder())
        assert dm.check_fields_selected([None, "City"], "APPEND") in (True, False)
