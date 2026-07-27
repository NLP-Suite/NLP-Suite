"""Regression for the File Classifier secondary-INPUT-directory lockout Evan hit on Mac and Windows.

The RUN button was computed once, at GUI build time, from the config csv. A GUI needing a secondary
input directory (file_classifier, corpus_checker_PCACE_data) whose config csv had that row blank could
therefore never be unblocked from the GUI itself -- selecting the directory with the GUI button left
RUN dead, so the row had to be typed into NLP_default_IO_config.csv by hand.

config_util.remove_missing_IO_line is the pure part of the fix: it drops the line for a value the user
just supplied on the GUI and reports whether anything else is still missing.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# conftest stubs config_util (it is infra for other modules under test); this file tests the real one.
sys.modules.pop('config_util', None)
import config_util  # noqa: E402

SECONDARY = 'Input files secondary directory'
OUTPUT = 'Output files directory'


class TestRemoveMissingIOLine:
    def test_the_only_missing_value_clears_the_whole_list(self):
        # this is Evan's case: RUN must come back on once the secondary directory is selected
        assert config_util.remove_missing_IO_line(SECONDARY + '\n', 'secondary') == ''

    def test_another_missing_value_keeps_the_list_non_empty(self):
        missing = SECONDARY + '\n' + OUTPUT + '\n'
        assert config_util.remove_missing_IO_line(missing, 'secondary') == OUTPUT + '\n'

    def test_a_non_matching_label_leaves_the_list_untouched(self):
        assert config_util.remove_missing_IO_line(OUTPUT + '\n', 'secondary') == OUTPUT + '\n'

    def test_the_match_is_case_insensitive(self):
        assert config_util.remove_missing_IO_line(SECONDARY + '\n', 'SECONDARY') == ''

    def test_an_empty_missing_list_stays_empty(self):
        assert config_util.remove_missing_IO_line('', 'secondary') == ''

    def test_an_empty_label_removes_nothing(self):
        assert config_util.remove_missing_IO_line(SECONDARY + '\n', '') == SECONDARY + '\n'

    def test_blank_lines_are_dropped_not_counted_as_still_missing(self):
        # a trailing '\n' must not read as a leftover missing value and keep RUN disabled
        assert config_util.remove_missing_IO_line(SECONDARY + '\n\n', 'secondary') == ''

    def test_every_remaining_line_is_preserved_in_order(self):
        missing = 'Input txt filename with path\n' + SECONDARY + '\n' + OUTPUT + '\n'
        expected = 'Input txt filename with path\n' + OUTPUT + '\n'
        assert config_util.remove_missing_IO_line(missing, 'secondary') == expected


class TestGetMissingIOValues:
    """The secondary directory must be reported missing only when the GUI actually asks for one."""

    @staticmethod
    def _alphabetic(secondary_path):
        return [['Input txt filename with path', '', '', '', '0'],
                ['Input files directory', 'C:/corpus', '', '', '0'],
                [SECONDARY, secondary_path, '', '', '0'],
                [OUTPUT, 'C:/out', '', '', '0']]

    def test_missing_secondary_dir_is_reported_for_a_GUI_that_needs_one(self):
        # file_classifier_main declares [1, 1, 1, 1]
        missing = config_util.get_missing_IO_values([1, 1, 1, 1], self._alphabetic(''))
        assert SECONDARY in missing

    def test_a_filled_secondary_dir_is_not_reported(self):
        missing = config_util.get_missing_IO_values([1, 1, 1, 1], self._alphabetic('C:/targets'))
        assert missing == ''

    def test_a_GUI_with_no_secondary_dir_ignores_the_blank_row(self):
        missing = config_util.get_missing_IO_values([1, 1, 0, 1], self._alphabetic(''))
        assert missing == ''
