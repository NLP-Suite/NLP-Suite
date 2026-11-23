"""Tests for src/config_util.py, one file per module (folded from 3 files, 23 Nov 2026).

From test_config_util_date_options.py:

get_date_options must not crash when there is no I/O config file yet (a first run).

With no config file, read_config_file returns template rows of five fields, [label, "", "", "", 0];
a saved config has six (label, path, sort order, separator, date format, date position). The date
check read row[4] (the integer 0 in a template row, never equal to "") as a date format and then
row[5], so Sample corpus crashed at open with IndexError on a first run from source.

From test_config_util_missing_IO.py:

Regression for the File Classifier secondary-INPUT-directory lockout Evan hit on Mac and Windows.

The RUN button was computed once, at GUI build time, from the config csv. A GUI needing a secondary
input directory (file_classifier, corpus_checker_PCACE_data) whose config csv had that row blank could
therefore never be unblocked from the GUI itself -- selecting the directory with the GUI button left
RUN dead, so the row had to be typed into NLP_default_IO_config.csv by hand.

config_util.remove_missing_IO_line is the pure part of the fix: it drops the line for a value the user
just supplied on the GUI and reports whether anything else is still missing.

From test_config_util_relative_paths.py:

Relative paths in an I/O config csv resolve against the NLP Suite folder, not the current folder.

lib/config_defaults/NLP_default_IO_config.csv (copied into config/ by the zip build) stores
`lib/sampleData/newspaperArticles` and `NLP_output`. Importing IO_files_util changes the current
folder to src/, so those paths were looked up under src/ and Shape of Stories crashed at open with
FileNotFoundError.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# conftest stubs config_util (it is infra for other modules under test); this file tests the real one.
sys.modules.pop("config_util", None)
import config_util  # noqa: E402

CONFIG = "NLP_default_IO_config.csv"
NUMERIC = [0, 1, 0, 1]  # input dir + output dir, as Sample corpus asks
DEFAULTS = (0, "mm/dd/yyyy", "_", 2)


def _use_config_dir(monkeypatch, path):
    monkeypatch.setattr(config_util.GUI_IO_util, "configPath", str(path), raising=False)
    monkeypatch.setattr(config_util.GUI_IO_util, "NLPPath", str(path), raising=False)


def _write_config(path, input_dir_row):
    rows = [
        "I/O File type,Path,Sort order,Date separator,Date format,Date position",
        "Input txt filename with path,,,,,",
        input_dir_row,
        "Input files secondary directory,,,,,",
        "Output files directory,/out,,,,",
    ]
    (path / CONFIG).write_text("\n".join(rows) + "\n", encoding="utf-8")


class TestGetDateOptions:
    def test_no_config_file_gives_the_defaults(self, tmp_path, monkeypatch):
        _use_config_dir(monkeypatch, tmp_path)
        result = config_util.get_date_options(CONFIG, NUMERIC)
        assert result == DEFAULTS + (False,)

    def test_a_saved_config_with_a_date_is_read(self, tmp_path, monkeypatch):
        _use_config_dir(monkeypatch, tmp_path)
        _write_config(tmp_path, "Input files directory,/corpus,0,-,dd-mm-yyyy,3")
        result = config_util.get_date_options(CONFIG, NUMERIC)
        assert result == (1, "dd-mm-yyyy", "-", 3, True)

    def test_a_saved_config_without_a_date_gives_the_defaults(self, tmp_path, monkeypatch):
        _use_config_dir(monkeypatch, tmp_path)
        _write_config(tmp_path, "Input files directory,/corpus,0,,,")
        result = config_util.get_date_options(CONFIG, NUMERIC)
        assert result == DEFAULTS + (True,)


# ---- formerly tests/test_config_util_missing_IO.py ----------------------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# conftest stubs config_util (it is infra for other modules under test); this file tests the real one.
sys.modules.pop("config_util", None)

SECONDARY = "Input files secondary directory"
OUTPUT = "Output files directory"


class TestRemoveMissingIOLine:
    def test_the_only_missing_value_clears_the_whole_list(self):
        # this is Evan's case: RUN must come back on once the secondary directory is selected
        assert config_util.remove_missing_IO_line(SECONDARY + "\n", "secondary") == ""

    def test_another_missing_value_keeps_the_list_non_empty(self):
        missing = SECONDARY + "\n" + OUTPUT + "\n"
        assert config_util.remove_missing_IO_line(missing, "secondary") == OUTPUT + "\n"

    def test_a_non_matching_label_leaves_the_list_untouched(self):
        assert config_util.remove_missing_IO_line(OUTPUT + "\n", "secondary") == OUTPUT + "\n"

    def test_the_match_is_case_insensitive(self):
        assert config_util.remove_missing_IO_line(SECONDARY + "\n", "SECONDARY") == ""

    def test_an_empty_missing_list_stays_empty(self):
        assert config_util.remove_missing_IO_line("", "secondary") == ""

    def test_an_empty_label_removes_nothing(self):
        assert config_util.remove_missing_IO_line(SECONDARY + "\n", "") == SECONDARY + "\n"

    def test_blank_lines_are_dropped_not_counted_as_still_missing(self):
        # a trailing '\n' must not read as a leftover missing value and keep RUN disabled
        assert config_util.remove_missing_IO_line(SECONDARY + "\n\n", "secondary") == ""

    def test_every_remaining_line_is_preserved_in_order(self):
        missing = "Input txt filename with path\n" + SECONDARY + "\n" + OUTPUT + "\n"
        expected = "Input txt filename with path\n" + OUTPUT + "\n"
        assert config_util.remove_missing_IO_line(missing, "secondary") == expected


class TestGetMissingIOValues:
    """The secondary directory must be reported missing only when the GUI actually asks for one."""

    @staticmethod
    def _alphabetic(secondary_path):
        return [
            ["Input txt filename with path", "", "", "", "0"],
            ["Input files directory", "C:/corpus", "", "", "0"],
            [SECONDARY, secondary_path, "", "", "0"],
            [OUTPUT, "C:/out", "", "", "0"],
        ]

    def test_missing_secondary_dir_is_reported_for_a_GUI_that_needs_one(self):
        # file_classifier_main declares [1, 1, 1, 1]
        missing = config_util.get_missing_IO_values([1, 1, 1, 1], self._alphabetic(""))
        assert SECONDARY in missing

    def test_a_filled_secondary_dir_is_not_reported(self):
        missing = config_util.get_missing_IO_values([1, 1, 1, 1], self._alphabetic("C:/targets"))
        assert missing == ""

    def test_a_GUI_with_no_secondary_dir_ignores_the_blank_row(self):
        missing = config_util.get_missing_IO_values([1, 1, 0, 1], self._alphabetic(""))
        assert missing == ""


# ---- formerly tests/test_config_util_relative_paths.py ------------------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# conftest stubs config_util (it is infra for other modules under test); this file tests the real one.
sys.modules.pop("config_util", None)

BASE = os.path.abspath(os.sep + os.path.join("suite", "NLP-Suite"))


def _rows(input_file="", input_dir="", secondary_dir="", output_dir=""):
    # rows as read_config_file returns them (header already dropped)
    return [
        ["Input txt filename with path", input_file, "", "", "", ""],
        ["Input files directory", input_dir, "0", "_", "mm/dd/yyyy", "4"],
        ["Input files secondary directory", secondary_dir, "", "", "", ""],
        ["Output files directory", output_dir, "", "", "", ""],
    ]


class TestResolveRelativeConfigPaths:
    def test_the_default_config_paths_resolve_under_the_suite_folder(self):
        rows = config_util.resolve_relative_config_paths(
            _rows(input_dir="lib/sampleData/newspaperArticles", output_dir="NLP_output"), BASE
        )
        assert rows[1][1] == os.path.join(BASE, "lib", "sampleData", "newspaperArticles")
        assert rows[3][1] == os.path.join(BASE, "NLP_output")

    def test_absolute_paths_are_left_alone(self):
        absolute = os.path.abspath(os.sep + os.path.join("Users", "me", "corpus"))
        rows = config_util.resolve_relative_config_paths(_rows(input_dir=absolute), BASE)
        assert rows[1][1] == absolute

    def test_blank_paths_stay_blank(self):
        rows = config_util.resolve_relative_config_paths(_rows(), BASE)
        assert [r[1] for r in rows] == ["", "", "", ""]

    def test_a_relative_input_file_resolves_too(self):
        rows = config_util.resolve_relative_config_paths(_rows(input_file="lib/sample.txt"), BASE)
        assert rows[0][1] == os.path.join(BASE, "lib", "sample.txt")

    def test_the_other_columns_are_not_touched(self):
        rows = config_util.resolve_relative_config_paths(_rows(input_dir="lib/x"), BASE)
        assert rows[1][0] == "Input files directory"
        assert rows[1][2:] == ["0", "_", "mm/dd/yyyy", "4"]

    def test_short_or_empty_rows_do_not_crash(self):
        assert config_util.resolve_relative_config_paths([[]], BASE) == [[]]
        assert config_util.resolve_relative_config_paths([["label only"]], BASE) == [["label only"]]
