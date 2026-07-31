"""Opening a file must never be able to kill the suite.

The Corpus Profiler died on os.startfile with "Fatal Python error: PyEval_RestoreThread: NULL
tstate" AFTER a seven-hour profile had written every one of its files. os.startfile runs
ShellExecute inside this process, so the handler's shell extensions - cloud-sync overlays,
antivirus hooks, whatever owns .html - are loaded into the Python interpreter, and one of them
taking the process down takes the run's last step with it.

open_in_desktop launches from a child process instead. These tests pin the two properties that
matter: nothing is ever run in-process before a child has been tried, and no failure escapes as an
exception to the caller.
"""
import importlib.util
import os
import subprocess
import sys
from unittest.mock import MagicMock

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')


@pytest.fixture
def io_files():
    spec = importlib.util.spec_from_file_location(
        '_io_open_desktop', os.path.join(_SRC, 'IO_files_util.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestItLaunchesOutOfProcess:
    def test_a_child_process_is_started(self, io_files, monkeypatch, tmp_path):
        f = tmp_path / 'summary.html'
        f.write_text('<p>hi</p>', encoding='utf-8')
        calls = []
        monkeypatch.setattr(io_files.subprocess, 'Popen',
                            lambda cmd, **kw: calls.append((cmd, kw)) or MagicMock())
        assert io_files.open_in_desktop(str(f)) is True
        assert len(calls) == 1, 'exactly one launch for a working handler'

    def test_os_startfile_is_NOT_reached_when_a_child_starts(self, io_files, monkeypatch, tmp_path):
        """The whole point. os.startfile is what crashed; it must be a last resort, not the path
        taken on a healthy machine."""
        f = tmp_path / 'summary.html'
        f.write_text('x', encoding='utf-8')
        monkeypatch.setattr(io_files.subprocess, 'Popen', lambda cmd, **kw: MagicMock())
        called = []
        monkeypatch.setattr(io_files.os, 'startfile', lambda p: called.append(p), raising=False)
        io_files.open_in_desktop(str(f))
        assert called == [], 'os.startfile ran even though a child process started'

    def test_it_falls_through_when_the_first_launcher_fails(self, io_files, monkeypatch, tmp_path):
        """One launcher missing must not sink it.

        How far it falls depends on the platform, and the test must not assume: Windows has two
        launchers to try before webbrowser, Linux and macOS have one. Asserting "the second Popen
        succeeds" passed on Windows and failed on Linux, where there is no second Popen and the
        real webbrowser.open was reached instead - which is how this file first broke CI.
        """
        f = tmp_path / 'summary.html'
        f.write_text('x', encoding='utf-8')
        seen = []

        def flaky(cmd, **kw):
            seen.append(cmd[0])
            if len(seen) == 1:
                raise OSError('no such launcher')
            return MagicMock()

        monkeypatch.setattr(io_files.subprocess, 'Popen', flaky)
        import webbrowser
        monkeypatch.setattr(webbrowser, 'open', lambda *a, **k: True)
        assert io_files.open_in_desktop(str(f)) is True
        assert seen, 'it never tried to launch anything'


class TestEveryPlatform:
    """The launchers differ per platform, so exercise each branch HERE rather than discovering it
    from a red CI run on an operating system nobody develops on."""

    @pytest.mark.parametrize('platform,expected', [
        ('win32', 'explorer.exe'),
        ('darwin', 'open'),
        ('linux', 'xdg-open'),
    ])
    def test_the_right_launcher_is_used(self, io_files, monkeypatch, tmp_path,
                                        platform, expected):
        f = tmp_path / 'summary.html'
        f.write_text('x', encoding='utf-8')
        monkeypatch.setattr(io_files.sys, 'platform', platform)
        got = []
        monkeypatch.setattr(io_files.subprocess, 'Popen',
                            lambda cmd, **kw: got.append(cmd) or MagicMock())
        assert io_files.open_in_desktop(str(f)) is True
        assert got and got[0][0] == expected

    @pytest.mark.parametrize('platform', ['win32', 'darwin', 'linux'])
    def test_a_failing_launcher_never_raises_on_any_platform(self, io_files, monkeypatch,
                                                             tmp_path, platform):
        f = tmp_path / 'summary.html'
        f.write_text('x', encoding='utf-8')
        monkeypatch.setattr(io_files.sys, 'platform', platform)
        monkeypatch.setattr(io_files.subprocess, 'Popen',
                            lambda *a, **k: (_ for _ in ()).throw(OSError('nope')))
        import webbrowser
        monkeypatch.setattr(webbrowser, 'open', lambda *a, **k: False)
        monkeypatch.setattr(io_files.os, 'startfile',
                            lambda p: (_ for _ in ()).throw(OSError('nope')), raising=False)
        assert io_files.open_in_desktop(str(f)) is False

    def test_nothing_waits_on_the_child(self, io_files, monkeypatch, tmp_path):
        """A launcher that blocks would hang the GUI at the end of a run. Popen must be fired and
        forgotten - no .wait(), no .communicate(), no check_call."""
        f = tmp_path / 'summary.html'
        f.write_text('x', encoding='utf-8')
        proc = MagicMock()
        monkeypatch.setattr(io_files.subprocess, 'Popen', lambda cmd, **kw: proc)
        for blocking in ('call', 'check_call', 'check_output', 'run'):
            monkeypatch.setattr(io_files.subprocess, blocking,
                                lambda *a, **k: pytest.fail('open_in_desktop blocked on the child'))
        io_files.open_in_desktop(str(f))
        proc.wait.assert_not_called()
        proc.communicate.assert_not_called()


class TestItNeverRaises:
    def test_every_launcher_failing_returns_False_not_an_exception(self, io_files, monkeypatch,
                                                                   tmp_path):
        """Called at the END of a run. An exception here would lose a finished profile to a
        traceback about opening a file."""
        f = tmp_path / 'summary.html'
        f.write_text('x', encoding='utf-8')
        monkeypatch.setattr(io_files.subprocess, 'Popen',
                            lambda *a, **k: (_ for _ in ()).throw(OSError('nope')))
        monkeypatch.setattr(io_files.os, 'startfile',
                            lambda p: (_ for _ in ()).throw(OSError('nope')), raising=False)
        import webbrowser
        monkeypatch.setattr(webbrowser, 'open', lambda *a, **k: False)
        assert io_files.open_in_desktop(str(f)) is False

    def test_a_path_that_does_not_exist_is_still_not_an_exception(self, io_files, monkeypatch):
        monkeypatch.setattr(io_files.subprocess, 'Popen', lambda cmd, **kw: MagicMock())
        assert io_files.open_in_desktop('Z:\\nowhere\\gone.html') in (True, False)

    def test_a_weird_path_does_not_blow_up_the_quoting(self, io_files, monkeypatch, tmp_path):
        """Output folders carry corpus names with spaces, ampersands and brackets."""
        odd = tmp_path / 'corpus (a & b) [2024]'
        odd.mkdir()
        f = odd / 'NLP_corpus_profile_summary.html'
        f.write_text('x', encoding='utf-8')
        got = []
        monkeypatch.setattr(io_files.subprocess, 'Popen',
                            lambda cmd, **kw: got.append(cmd) or MagicMock())
        assert io_files.open_in_desktop(str(f)) is True
        # the path travels as its OWN argv element - never concatenated into a command string,
        # which is where '&' would end the command and run the rest
        assert any(str(f) in part for part in got[0])
        assert all(isinstance(part, str) for part in got[0])


@pytest.mark.skipif(sys.platform != 'win32', reason='Windows launcher details')
class TestOnWindows:
    def test_it_does_not_open_a_console_window(self, io_files, monkeypatch, tmp_path):
        """The suite runs under pythonw and as a frozen build; a flashing console at the end of a
        run looks like a crash."""
        f = tmp_path / 'summary.html'
        f.write_text('x', encoding='utf-8')
        kwargs = {}
        monkeypatch.setattr(io_files.subprocess, 'Popen',
                            lambda cmd, **kw: kwargs.update(kw) or MagicMock())
        io_files.open_in_desktop(str(f))
        assert kwargs.get('creationflags', 0) & getattr(
            subprocess, 'CREATE_NO_WINDOW', 0x08000000)
