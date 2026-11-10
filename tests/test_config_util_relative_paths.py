"""Relative paths in an I/O config csv resolve against the NLP Suite folder, not the current folder.

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
