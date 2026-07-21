"""Regressions for the three bugs Evan found testing v1.6.30 on Mac and Windows."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import data_manipulation_util as dm  # noqa: E402


class _Recorder:
    def __init__(self):
        self.warnings = []

    def showwarning(self, title, message):
        self.warnings.append((title, message))


class TestAppendEmptyField:
    """APPEND raised KeyError: '' when a listed file had no field selected."""

    def test_empty_field_is_rejected_with_a_message(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(dm, 'mb', rec)
        assert dm.check_fields_selected(['Year', ''], 'APPEND') is False
        assert len(rec.warnings) == 1
        title, message = rec.warnings[0]
        assert 'APPEND' in message
        assert 'field' in message.lower()

    def test_whitespace_only_field_is_rejected(self, monkeypatch):
        monkeypatch.setattr(dm, 'mb', _Recorder())
        assert dm.check_fields_selected(['Year', '   '], 'APPEND') is False

    def test_all_fields_present_passes_silently(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(dm, 'mb', rec)
        assert dm.check_fields_selected(['Year', 'City'], 'APPEND') is True
        assert rec.warnings == []

    def test_a_single_record_is_handled(self, monkeypatch):
        monkeypatch.setattr(dm, 'mb', _Recorder())
        assert dm.check_fields_selected([''], 'APPEND') is False
        assert dm.check_fields_selected(['Year'], 'APPEND') is True

    def test_append_returns_empty_instead_of_raising(self, monkeypatch):
        # the record shape the GUI builds when no field was picked: 'path,'
        monkeypatch.setattr(dm, 'mb', _Recorder())
        assert dm.append('/tmp', ['C:/corpus/data.csv,']) == ''

    def test_concatenate_is_guarded_too(self, monkeypatch):
        monkeypatch.setattr(dm, 'mb', _Recorder())
        assert dm.concatenate('/tmp', ['C:/corpus/data.csv,', 'C:/corpus/other.csv,']) == ''

    def test_non_string_headers_do_not_crash_the_check(self, monkeypatch):
        monkeypatch.setattr(dm, 'mb', _Recorder())
        assert dm.check_fields_selected([None, 'City'], 'APPEND') in (True, False)
