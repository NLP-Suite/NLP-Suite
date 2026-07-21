"""Tests for the model-download failure reporting.

The behaviour under test is what an inexperienced user sees when a language model cannot be
downloaded: previously a ConnectionError reached the terminal only and the process exited, so someone
running the Suite from the app saw the window vanish with no explanation.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import IO_internet_util as net  # noqa: E402


class _Recorder:
    """Stands in for tkinter.messagebox, recording what the user would have been shown."""

    def __init__(self, answer=True):
        self.errors = []
        self.answer = answer

    def showerror(self, title, message):
        self.errors.append((title, message))

    def showwarning(self, title, message):
        self.errors.append((title, message))

    def askyesno(self, title, message):
        return self.answer


def _offline(monkeypatch, answer=True):
    rec = _Recorder(answer)
    monkeypatch.setattr(net, 'mb', rec)
    monkeypatch.setattr(net, 'internet_on', lambda: False)
    return rec


def _boom():
    raise ConnectionError('getaddrinfo failed')


class TestDownloadWithWarning:
    def test_success_is_silent(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, 'mb', rec)
        monkeypatch.setattr(net, 'internet_on', lambda: True)
        assert net.download_with_warning('x', lambda: None) is True
        assert rec.errors == []

    def test_retries_once_when_the_user_bypasses_the_check(self, monkeypatch):
        _offline(monkeypatch, answer=True)
        calls = []
        def fn():
            calls.append(1)
            raise ConnectionError('getaddrinfo failed')
        net.download_with_warning('x', fn)
        # the old code offered the bypass but never tried again, so answering Yes changed nothing
        assert len(calls) == 2

    def test_retry_can_succeed(self, monkeypatch):
        _offline(monkeypatch, answer=True)
        state = {'n': 0}
        def fn():
            state['n'] += 1
            if state['n'] == 1:
                raise ConnectionError('transient')
        assert net.download_with_warning('x', fn) is True

    def test_reports_failure_and_returns_false(self, monkeypatch):
        rec = _offline(monkeypatch, answer=True)
        assert net.download_with_warning('x', _boom) is False
        assert len(rec.errors) == 1

    def test_declining_the_bypass_still_reports(self, monkeypatch):
        rec = _offline(monkeypatch, answer=False)
        assert net.download_with_warning('x', _boom) is False
        assert len(rec.errors) == 1

    def test_only_one_dialog_beyond_the_yes_no_question(self, monkeypatch):
        rec = _offline(monkeypatch, answer=True)
        net.download_with_warning('x', _boom)
        assert len(rec.errors) == 1


class TestReportDownloadFailure:
    def test_message_carries_the_real_exception(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, 'mb', rec)
        net.report_download_failure('Stanza_functions_util.py', ConnectionError('getaddrinfo failed'))
        _, message = rec.errors[0]
        assert 'ConnectionError' in message
        assert 'getaddrinfo failed' in message

    def test_message_names_the_script_and_says_what_to_do(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, 'mb', rec)
        net.report_download_failure('wordclouds_util.py', OSError('nope'), 'the Stanza English language model')
        _, message = rec.errors[0]
        assert 'wordclouds_util.py' in message
        assert 'the Stanza English language model' in message
        assert 'WHAT TO DO' in message

    def test_suggests_the_firewall_and_alternative_package_routes(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, 'mb', rec)
        net.report_download_failure('x', OSError('nope'))
        _, message = rec.errors[0]
        assert 'raw.githubusercontent.com' in message
        assert 'spaCy' in message
