"""Tests for src/IO_files_util.py, one file per module (folded from 6 files, 23 Nov 2026).

From test_cmap_guard.py:

A crafted pdf must not be able to make pdfminer unpickle a file of its choosing.

pdfminer builds "<name>.pickle.gz" from a CMap name taken out of the pdf and os.path.join()s it
onto its own cmap directory - and os.path.join DISCARDS the directory when what follows is
absolute. So "\\\\attacker\\share\\evil", "C:/tmp/evil" or "../../evil" lands wherever the attacker
likes, and pdfminer then pickle.loads() it. Loading a pickle runs whatever code it carries:
GHSA-wf5f-4jwr-ppcp, CVSS 8.6, arbitrary code execution from opening a pdf. On Windows the path can
be a NETWORK location, so nothing needs planting on the machine first.

Fixed upstream in pdfminer.six 20251107, which requires Python >= 3.9. This suite runs 3.8, where
the newest available is 20250324 - the fix cannot be installed, hence the guard.

The name check is a pure function over strings, so the hostile inputs are just strings and this
whole file runs without pdfminer installed.

From test_file_order_date_fallback.py:

Input files whose names do not all carry a date in the configured place keep the 1.6.45 order (alphabetical).

getFileList sorts by the filename settings of the I/O configuration (separator, date format, date position),
through IO_files_util.do_compare, and falls back to alphabetical order when that comparison fails. Until #1774
the comparison's error handler itself raised NameError (`date_location`), so a failure always reached the
fallback. #1774 fixed the name, and the handler then returned -1 for any pair, an inconsistent comparison
that left the files in arbitrary order: Shape of Stories on the 5 sample reviews plus the 5 sample stories got
its documents in a different order, and different clusters, in the 1.6.46 candidate (tool_sweep, 23 Nov).

From test_open_in_desktop.py:

Opening a file must never be able to kill the suite.

The Corpus Profiler died on os.startfile with "Fatal Python error: PyEval_RestoreThread: NULL
tstate" AFTER a seven-hour profile had written every one of its files. os.startfile runs
ShellExecute inside this process, so the handler's shell extensions - cloud-sync overlays,
antivirus hooks, whatever owns .html - are loaded into the Python interpreter, and one of them
taking the process down takes the run's last step with it.

open_in_desktop launches from a child process instead. These tests pin the two properties that
matter: nothing is ever run in-process before a child has been tried, and no failure escapes as an
exception to the caller.

From test_output_dir_missing_parent.py:

An output subfolder is made even when the output folder itself does not exist yet.

The zip's default config (lib/config_defaults) sends output to NLP_output inside the NLP Suite folder,
but nothing creates that folder. make_output_subdirectory and make_directory chmod-ed the parent and
then os.mkdir-ed the subfolder, so on a fresh install the first RUN of almost every tool stopped with
"Could not create the directory .../NLP_output/<label>_<input> [Errno 2] No such file or directory".

From test_output_file_names.py:

Output filenames: labels are added once, and the name still says everything it did.

A tool's output becomes the next tool's input, so the input filename already carries the labels
of every step that made it. Adding them again produced names like

    NLP_GIS_GIS_GIS_CoreNLP_NER_ALL_NER_Dir_<corpus>_geo-Goo_Location_distance_pairwise_...

162 characters before the folders above it — and on Windows a path over 260 characters cannot be
copied. The co-author on the Harry Potter paper hit exactly that, with a dialog whose Skip button
would have silently dropped the files.

From test_output_file_name_calls.py:

No call to IO_files_util.generate_output_file_name has an extension where a folder belongs.

Its arguments are (inputFilename, inputDir, outputDir, outputExtension, labels...). A call that left out
inputDir, as Semantic aggregation's "Aggregate by sentence index" did (#1780), passes the output folder as
inputDir and ".csv" as outputDir, and pandas then stops with "Cannot save file into a non-existent directory:
'.csv'". This parses src/ (no imports) and lists calls with a ".xyz" string in the inputDir or outputDir slot.
"""

import importlib.util
import os
import sys

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)


@pytest.fixture(scope="module")
def io_files():
    spec = importlib.util.spec_from_file_location("_io_cmap_guard", os.path.join(_SRC, "IO_files_util.py"))
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


class TestNamesThatEscape:
    """Every one of these resolves OUTSIDE pdfminer's cmap directory."""

    @pytest.mark.parametrize(
        "name",
        [
            r"\\attacker\share\evil",  # UNC: the Windows remote case, no local file needed
            "//attacker/share/evil",
            "C:/Windows/Temp/evil",
            r"C:\Windows\Temp\evil",
            "c:evil",  # drive-relative
            "../../../../Users/Public/evil",
            r"..\..\evil",
            "/tmp/evil",
            "/etc/passwd",
            "~/evil",
            "UniJIS-UCS2-H/../../evil",
            "sub/dir/evil",
            r"sub\dir\evil",
        ],
    )
    def test_it_is_refused(self, io_files, name):
        assert io_files.is_safe_cmap_name(name) is False


class TestNamesThatAreJustWrong:
    @pytest.mark.parametrize(
        "name",
        [
            "",
            ".",
            "..",
            "x" * 129,
            " ",
            "a name with spaces",
            "evil\x00",
            "evil\x00.pickle.gz",
            "-leading-dash",
            ".hidden",
            "na\nme",
        ],
    )
    def test_it_is_refused(self, io_files, name):
        assert io_files.is_safe_cmap_name(name) is False

    @pytest.mark.parametrize("name", [None, 42, b"bytes-not-str", ["a"], object()])
    def test_a_non_string_is_refused_rather_than_crashing(self, io_files, name):
        """It is called from inside pdfminer with whatever the pdf contained."""
        assert io_files.is_safe_cmap_name(name) is False


class TestRealCMapNamesStillWork:
    """A whitelist that blocked a legitimate name would quietly degrade text extraction for
    Japanese, Chinese and Korean pdfs - a silent loss, and the worst possible outcome here."""

    @pytest.mark.parametrize(
        "name",
        [
            "UniJIS-UCS2-H",
            "UniJIS-UCS2-V",
            "90ms-RKSJ-H",
            "78-EUC-V",
            "Adobe-Japan1-UCS2",
            "B5pc-H",
            "ETen-B5-H",
            "KSCms-UHC-HW-V",
            "UniGB-UCS2-H",
            "Identity-H",
            "to-unicode-Adobe-Japan1",
            "to-unicode-Adobe-Korea1",
            "Add-RKSJ-H",
            "EUC-H",
            "Hankaku",
            "Roman",
            "WP-Symbol",
            "Ext-RKSJ-V",
            "UniKS-UTF16-H",
        ],
    )
    def test_it_is_allowed(self, io_files, name):
        assert io_files.is_safe_cmap_name(name) is True

    def test_every_cmap_pdfminer_actually_ships_is_allowed(self, io_files):
        """The real test set, not a sample of it. Skipped when pdfminer is absent (CI)."""
        try:
            from pdfminer import cmapdb
        except Exception:
            pytest.skip("pdfminer not installed")
        cmap_dir = os.path.join(os.path.dirname(cmapdb.__file__), "cmap")
        if not os.path.isdir(cmap_dir):
            pytest.skip("no bundled cmap directory")
        # pdfminer.six shipped its cmaps as .pickle.gz until 2025 and as .json.gz from 20260107 on.
        suffixes = (".pickle.gz", ".json.gz")
        names = [f[: -len(sfx)] for f in os.listdir(cmap_dir) for sfx in suffixes if f.endswith(sfx)]
        assert names, "no bundled cmaps found to check against"
        rejected = [n for n in names if not io_files.is_safe_cmap_name(n)]
        assert rejected == [], f"the guard would break these real pdfs: {rejected[:10]}"
        # the unicode maps are looked up with a prefix
        prefixed = [n for n in (f"to-unicode-{n}" for n in names) if not io_files.is_safe_cmap_name(n)]
        assert prefixed == []


class TestTheGuardIsWiredIn:
    def test_installing_it_is_idempotent(self, io_files):
        pytest.importorskip("pdfminer.cmapdb", reason="pdfminer not installed")
        from pdfminer.cmapdb import CMapDB

        assert io_files.harden_pdfminer_cmap() is True
        first = CMapDB._load_data
        assert getattr(first, "_nlp_suite_guarded", False)
        assert io_files.harden_pdfminer_cmap() is True
        assert getattr(CMapDB._load_data, "_nlp_suite_guarded", False)

    def test_a_hostile_name_raises_the_error_pdfminer_ALREADY_handles(self, io_files):
        """CMapNotFound is caught in pdffont and pdfinterp, so a hostile pdf degrades to slightly
        thinner text instead of ending the conversion."""
        pytest.importorskip("pdfminer.cmapdb", reason="pdfminer not installed")
        from pdfminer.cmapdb import CMapDB

        io_files.harden_pdfminer_cmap()
        with pytest.raises(CMapDB.CMapNotFound):
            CMapDB._load_data(r"\\attacker\share\evil")

    def test_a_real_cmap_still_loads(self, io_files):
        pytest.importorskip("pdfminer.cmapdb", reason="pdfminer not installed")
        from pdfminer.cmapdb import CMapDB

        io_files.harden_pdfminer_cmap()
        assert CMapDB._load_data("UniJIS-UCS2-H") is not None

    def test_the_converter_installs_it_before_opening_any_pdf(self):
        """Checked in the source: the call must sit at module level, next to the pdfminer imports,
        not inside a function that a code path might miss."""
        src = open(os.path.join(_SRC, "file_converter_util.py"), encoding="utf-8", errors="replace").read()
        assert "harden_pdfminer_cmap()" in src
        call_at = src.index("harden_pdfminer_cmap()")
        # before the first function that reads a pdf
        first_def = src.index("\ndef ")
        assert call_at < first_def, "the guard is installed after the module already defines readers"


# ---- formerly tests/test_file_order_date_fallback.py --------------------------------------------------------

# conftest stubs IO_files_util; load the real one under a private name, as the output-file-name tests below do
_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)
_spec = importlib.util.spec_from_file_location("_real_IO_files_util_order", os.path.join(_SRC, "IO_files_util.py"))
IO_files_util = importlib.util.module_from_spec(_spec)
_cwd = os.getcwd()
try:
    _spec.loader.exec_module(IO_files_util)  # it chdirs to src/ at import
finally:
    os.chdir(_cwd)

STORIES = [  # the sweep's "stories" input: 5 reviews with a date in item 4, 5 stories without one
    "Bunin - Gentle breath.txt",
    "Faulkner - Dry September.txt",
    "Murphy - Miracles thicker than fog.txt",
    "Professor Dumbass.txt",
    "The Three Little Pigs.txt",
    "A Spool of Blue Thread_Anne Tyler_Rebecca Pepper Sinkler_02-13-2015.txt",
    "Barkskins_Annie Proulx_William T Vollmann_06-17-2016.txt",
    "Career of Evil_JK Rowling_Charles Finch_10-29-2015.txt",
    "Sweetbitter_Stephanie Danler_Gabrielle Hamilton_05-24-2016.txt",
    "The Fixer_Joseph Finder_Ken Tucker_06-10-2015.txt",
]
DEFAULT_IO = dict(sort_order="0", separator="_", date_format="mm/dd/yyyy", date_pos=4)  # lib/config_defaults


def test_a_corpus_the_date_order_cannot_sort_comes_back_alphabetical():
    for start in (STORIES, list(reversed(STORIES)), STORIES[3:] + STORIES[:3]):
        assert IO_files_util.sort_by_filename_settings(list(start), ".txt", **DEFAULT_IO) == sorted(STORIES)


def test_a_dated_corpus_sorts_the_same_whatever_order_the_files_come_in():
    dated = STORIES[5:]
    first = IO_files_util.sort_by_filename_settings(list(dated), ".txt", **DEFAULT_IO)
    assert sorted(first) == sorted(dated)
    for start in (list(reversed(dated)), dated[2:] + dated[:2]):
        assert IO_files_util.sort_by_filename_settings(list(start), ".txt", **DEFAULT_IO) == first


# ---- formerly tests/test_open_in_desktop.py -----------------------------------------------------------------

import subprocess  # noqa: E402
from unittest.mock import MagicMock  # noqa: E402

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


@pytest.fixture
def io_files_open_in_desktop():
    spec = importlib.util.spec_from_file_location("_io_open_desktop", os.path.join(_SRC, "IO_files_util.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestItLaunchesOutOfProcess:
    def test_a_child_process_is_started(self, io_files_open_in_desktop, monkeypatch, tmp_path):
        f = tmp_path / "summary.html"
        f.write_text("<p>hi</p>", encoding="utf-8")
        calls = []
        monkeypatch.setattr(
            io_files_open_in_desktop.subprocess, "Popen", lambda cmd, **kw: calls.append((cmd, kw)) or MagicMock()
        )
        assert io_files_open_in_desktop.open_in_desktop(str(f)) is True
        assert len(calls) == 1, "exactly one launch for a working handler"

    def test_os_startfile_is_NOT_reached_when_a_child_starts(self, io_files_open_in_desktop, monkeypatch, tmp_path):
        """The whole point. os.startfile is what crashed; it must be a last resort, not the path
        taken on a healthy machine."""
        f = tmp_path / "summary.html"
        f.write_text("x", encoding="utf-8")
        monkeypatch.setattr(io_files_open_in_desktop.subprocess, "Popen", lambda cmd, **kw: MagicMock())
        called = []
        monkeypatch.setattr(io_files_open_in_desktop.os, "startfile", lambda p: called.append(p), raising=False)
        io_files_open_in_desktop.open_in_desktop(str(f))
        assert called == [], "os.startfile ran even though a child process started"

    def test_it_falls_through_when_the_first_launcher_fails(self, io_files_open_in_desktop, monkeypatch, tmp_path):
        """One launcher missing must not sink it.

        How far it falls depends on the platform, and the test must not assume: Windows has two
        launchers to try before webbrowser, Linux and macOS have one. Asserting "the second Popen
        succeeds" passed on Windows and failed on Linux, where there is no second Popen and the
        real webbrowser.open was reached instead - which is how this file first broke CI.
        """
        f = tmp_path / "summary.html"
        f.write_text("x", encoding="utf-8")
        seen = []

        def flaky(cmd, **kw):
            seen.append(cmd[0])
            if len(seen) == 1:
                raise OSError("no such launcher")
            return MagicMock()

        monkeypatch.setattr(io_files_open_in_desktop.subprocess, "Popen", flaky)
        import webbrowser

        monkeypatch.setattr(webbrowser, "open", lambda *a, **k: True)
        assert io_files_open_in_desktop.open_in_desktop(str(f)) is True
        assert seen, "it never tried to launch anything"


class TestEveryPlatform:
    """The launchers differ per platform, so exercise each branch HERE rather than discovering it
    from a red CI run on an operating system nobody develops on."""

    @pytest.mark.parametrize(
        "platform,expected",
        [
            ("win32", "explorer.exe"),
            ("darwin", "open"),
            ("linux", "xdg-open"),
        ],
    )
    def test_the_right_launcher_is_used(self, io_files_open_in_desktop, monkeypatch, tmp_path, platform, expected):
        f = tmp_path / "summary.html"
        f.write_text("x", encoding="utf-8")
        monkeypatch.setattr(io_files_open_in_desktop.sys, "platform", platform)
        got = []
        monkeypatch.setattr(
            io_files_open_in_desktop.subprocess, "Popen", lambda cmd, **kw: got.append(cmd) or MagicMock()
        )
        assert io_files_open_in_desktop.open_in_desktop(str(f)) is True
        assert got and got[0][0] == expected

    @pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
    def test_a_failing_launcher_never_raises_on_any_platform(
        self, io_files_open_in_desktop, monkeypatch, tmp_path, platform
    ):
        f = tmp_path / "summary.html"
        f.write_text("x", encoding="utf-8")
        monkeypatch.setattr(io_files_open_in_desktop.sys, "platform", platform)
        monkeypatch.setattr(
            io_files_open_in_desktop.subprocess, "Popen", lambda *a, **k: (_ for _ in ()).throw(OSError("nope"))
        )
        import webbrowser

        monkeypatch.setattr(webbrowser, "open", lambda *a, **k: False)
        monkeypatch.setattr(
            io_files_open_in_desktop.os, "startfile", lambda p: (_ for _ in ()).throw(OSError("nope")), raising=False
        )
        assert io_files_open_in_desktop.open_in_desktop(str(f)) is False

    def test_nothing_waits_on_the_child(self, io_files_open_in_desktop, monkeypatch, tmp_path):
        """A launcher that blocks would hang the GUI at the end of a run. Popen must be fired and
        forgotten - no .wait(), no .communicate(), no check_call."""
        f = tmp_path / "summary.html"
        f.write_text("x", encoding="utf-8")
        proc = MagicMock()
        monkeypatch.setattr(io_files_open_in_desktop.subprocess, "Popen", lambda cmd, **kw: proc)
        for blocking in ("call", "check_call", "check_output", "run"):
            monkeypatch.setattr(
                io_files_open_in_desktop.subprocess,
                blocking,
                lambda *a, **k: pytest.fail("open_in_desktop blocked on the child"),
            )
        io_files_open_in_desktop.open_in_desktop(str(f))
        proc.wait.assert_not_called()
        proc.communicate.assert_not_called()


class TestItNeverRaises:
    def test_every_launcher_failing_returns_False_not_an_exception(
        self, io_files_open_in_desktop, monkeypatch, tmp_path
    ):
        """Called at the END of a run. An exception here would lose a finished profile to a
        traceback about opening a file."""
        f = tmp_path / "summary.html"
        f.write_text("x", encoding="utf-8")
        monkeypatch.setattr(
            io_files_open_in_desktop.subprocess, "Popen", lambda *a, **k: (_ for _ in ()).throw(OSError("nope"))
        )
        monkeypatch.setattr(
            io_files_open_in_desktop.os, "startfile", lambda p: (_ for _ in ()).throw(OSError("nope")), raising=False
        )
        import webbrowser

        monkeypatch.setattr(webbrowser, "open", lambda *a, **k: False)
        assert io_files_open_in_desktop.open_in_desktop(str(f)) is False

    def test_a_path_that_does_not_exist_is_still_not_an_exception(self, io_files_open_in_desktop, monkeypatch):
        monkeypatch.setattr(io_files_open_in_desktop.subprocess, "Popen", lambda cmd, **kw: MagicMock())
        assert io_files_open_in_desktop.open_in_desktop("Z:\\nowhere\\gone.html") in (True, False)

    def test_a_weird_path_does_not_blow_up_the_quoting(self, io_files_open_in_desktop, monkeypatch, tmp_path):
        """Output folders carry corpus names with spaces, ampersands and brackets."""
        odd = tmp_path / "corpus (a & b) [2024]"
        odd.mkdir()
        f = odd / "NLP_corpus_profile_summary.html"
        f.write_text("x", encoding="utf-8")
        got = []
        monkeypatch.setattr(
            io_files_open_in_desktop.subprocess, "Popen", lambda cmd, **kw: got.append(cmd) or MagicMock()
        )
        assert io_files_open_in_desktop.open_in_desktop(str(f)) is True
        # the path travels as its OWN argv element - never concatenated into a command string,
        # which is where '&' would end the command and run the rest
        assert any(str(f) in part for part in got[0])
        assert all(isinstance(part, str) for part in got[0])


@pytest.mark.skipif(sys.platform != "win32", reason="Windows launcher details")
class TestOnWindows:
    def test_it_does_not_open_a_console_window(self, io_files_open_in_desktop, monkeypatch, tmp_path):
        """The suite runs under pythonw and as a frozen build; a flashing console at the end of a
        run looks like a crash."""
        f = tmp_path / "summary.html"
        f.write_text("x", encoding="utf-8")
        kwargs = {}
        monkeypatch.setattr(
            io_files_open_in_desktop.subprocess, "Popen", lambda cmd, **kw: kwargs.update(kw) or MagicMock()
        )
        io_files_open_in_desktop.open_in_desktop(str(f))
        assert kwargs.get("creationflags", 0) & getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


# ---- formerly tests/test_output_dir_missing_parent.py -------------------------------------------------------

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)


def _load():
    spec = importlib.util.spec_from_file_location("_real_IO_files_util", os.path.join(_SRC, "IO_files_util.py"))
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


io_files_output_dir_missing_parent = _load()


def test_output_subdirectory_under_a_missing_output_folder(tmp_path):
    output_dir = tmp_path / "NLP_output"  # not created, as on a fresh install
    sub = io_files_output_dir_missing_parent.make_output_subdirectory(
        "", str(tmp_path / "newspaperArticles"), str(output_dir), "Lemma_Stanza"
    )
    assert sub == str(output_dir / "Lemma_Stanza_newspaperArticles")
    assert os.path.isdir(sub)


def test_output_subdirectory_under_an_existing_output_folder(tmp_path):
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    sub = io_files_output_dir_missing_parent.make_output_subdirectory(
        "", str(tmp_path / "corpus"), str(output_dir), "NER"
    )
    assert sub == str(output_dir / "NER_corpus")
    assert os.path.isdir(sub)


def test_make_directory_under_a_missing_parent(tmp_path):
    target = tmp_path / "missing" / "new"
    assert io_files_output_dir_missing_parent.make_directory(str(target)) == str(target)
    assert os.path.isdir(target)


# ---- formerly tests/test_output_file_names.py ---------------------------------------------------------------

# conftest replaces IO_files_util with a MagicMock for the whole session, because most modules under
# test only import it for side effects. Here it IS the module under test, so the real one is loaded
# from source under a private name - its own imports (GUI_util, IO_libraries_util, pandas...) still
# resolve against the stubs, and sys.modules['IO_files_util'] stays the stub for every other test.
_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, _SRC)
_spec_output_file_names = importlib.util.spec_from_file_location(
    "_real_IO_files_util", os.path.join(_SRC, "IO_files_util.py")
)
io = importlib.util.module_from_spec(_spec_output_file_names)

# IO_files_util does os.chdir(src) at import, so merely loading it moves the WHOLE test process into
# src/ and any later test using a relative path resolves it somewhere unexpected. Put the working
# directory back.
_cwd = os.getcwd()
try:
    _spec_output_file_names.loader.exec_module(io)
finally:
    os.chdir(_cwd)


class TestLabelAlreadyInName:
    def test_a_word_of_the_name_is_found(self):
        assert io.label_already_in_name("GIS", "NLP_GIS_Dir_corpus")

    def test_a_word_that_is_not_there_is_not_found(self):
        assert not io.label_already_in_name("SVO", "NLP_GIS_Dir_corpus")

    def test_it_compares_words_not_substrings(self):
        """'NER' is inside 'GENERAL'; a substring test would drop a label that belongs."""
        assert not io.label_already_in_name("NER", "NLP_GENERAL_Dir_corpus")
        assert not io.label_already_in_name("GIS", "NLP_AEGIS_Dir_corpus")

    def test_case_does_not_matter(self):
        assert io.label_already_in_name("ner", "NLP_NER_Dir_corpus")

    def test_a_multi_word_label_needs_the_whole_sequence(self):
        assert io.label_already_in_name("NER_ALL", "NLP_CoreNLP_NER_ALL_Dir_corpus")
        assert not io.label_already_in_name("NER_ALL", "NLP_NER_Dir_ALL_corpus")


class TestNamesDoNotAccumulate:
    def test_a_fresh_corpus_gets_its_label(self, tmp_path):
        out = io.generate_output_file_name("", str(tmp_path / "HPbooks"), str(tmp_path), ".csv", "GIS")
        assert os.path.basename(out) == "NLP_GIS_Dir_HPbooks.csv"

    def test_running_the_same_step_again_does_not_repeat_its_label(self, tmp_path):
        """The bug: GIS output fed back into GIS gave NLP_GIS_GIS_..."""
        first = io.generate_output_file_name("", str(tmp_path / "HPbooks"), str(tmp_path), ".csv", "GIS")
        second = io.generate_output_file_name(first, "", str(tmp_path), ".csv", "GIS")
        assert "GIS_GIS" not in os.path.basename(second)
        assert "GIS" in os.path.basename(second)

    def test_three_passes_do_not_treble_it(self, tmp_path):
        name = io.generate_output_file_name("", str(tmp_path / "HPbooks"), str(tmp_path), ".csv", "GIS")
        for _ in range(2):
            name = io.generate_output_file_name(name, "", str(tmp_path), ".csv", "GIS")
        assert os.path.basename(name).count("GIS") == 1

    def test_a_different_label_is_still_added(self, tmp_path):
        first = io.generate_output_file_name("", str(tmp_path / "HPbooks"), str(tmp_path), ".csv", "GIS")
        second = io.generate_output_file_name(first, "", str(tmp_path), ".csv", "NER")
        base = os.path.basename(second)
        assert "GIS" in base and "NER" in base

    def test_trailing_labels_are_not_repeated_either(self, tmp_path):
        """label2..label5 accumulated the same way — NER_ALL_NER in the real filename."""
        first = io.generate_output_file_name("", str(tmp_path / "HPbooks"), str(tmp_path), ".csv", "NER", "Location")
        second = io.generate_output_file_name(first, "", str(tmp_path), ".csv", "NER", "Location")
        assert os.path.basename(second).count("Location") == 1

    def test_the_name_still_carries_every_step(self, tmp_path):
        """Shorter must not mean less informative: everything that finds files by name
        (the reuse probes, the report, OpenOutputFiles) reads these words."""
        name = io.generate_output_file_name("", str(tmp_path / "HPbooks"), str(tmp_path), ".csv", "GIS", "Location")
        name = io.generate_output_file_name(name, "", str(tmp_path), ".csv", "NER", "distance")
        base = os.path.basename(name).lower()
        for word in ("gis", "location", "ner", "distance", "hpbooks"):
            assert word in base

    def test_the_real_case_gets_much_shorter(self, tmp_path):
        """The filename from the screenshot, rebuilt the way the pipeline builds it."""
        name = io.generate_output_file_name(
            "", str(tmp_path / "newspaperArticles"), str(tmp_path), ".csv", "GIS", "CoreNLP_NER_ALL"
        )
        for _ in range(2):
            name = io.generate_output_file_name(name, "", str(tmp_path), ".csv", "GIS", "NER")
        base = os.path.basename(name)
        assert "GIS_GIS" not in base
        assert "NER_ALL_NER" not in base
        assert len(base) < 80, base


class TestIllegalCharactersInLabels:
    """A label comes from a column header, and a column header can hold anything.

    'Sentence iconicity (Mean score: 1 Not iconic-7 Very iconic)' was used as a filename label. On
    Windows a colon opens an NTFS alternate data stream, so that wrote a ZERO-BYTE file named
    'NLP_Sentence iconicity (Mean score' with no extension and put the data in a stream nothing
    reads. The iconicity chart had been failing that way silently: the file exists, so nothing looks
    wrong until you open it.
    """

    def test_a_colon_becomes_a_dash(self):
        assert io.safe_filename_part("Mean score: 1 Not iconic") == "Mean score- 1 Not iconic"

    def test_slashes_cannot_reach_the_filesystem(self):
        """A slash would write into a subdirectory, or above one."""
        cleaned = io.safe_filename_part("a/b" + chr(92) + "c")
        assert "/" not in cleaned and chr(92) not in cleaned

    def test_every_character_windows_refuses(self):
        illegal = '<>:"/' + chr(92) + "|?*"
        cleaned = io.safe_filename_part("a".join(illegal))
        for ch in illegal:
            assert ch not in cleaned

    def test_a_trailing_dot_or_space_is_dropped(self):
        """Windows silently strips them, which turns two different names into one."""
        assert io.safe_filename_part("name. ") == "name"
        assert io.safe_filename_part("name ") == "name"

    def test_ordinary_text_is_untouched(self):
        assert io.safe_filename_part("NLP_SVO_Stanza_Dir_corpus") == "NLP_SVO_Stanza_Dir_corpus"

    def test_the_real_iconicity_label_produces_a_usable_name(self, tmp_path):
        name = io.generate_output_file_name(
            "",
            str(tmp_path / "HPbooks"),
            str(tmp_path),
            ".csv",
            "Sentence iconicity (Mean score: 1 Not iconic-7 Very iconic)",
        )
        assert ":" not in os.path.basename(name)
        assert os.path.basename(name).endswith(".csv")


class TestTheCorpusNameIsNotSaidThreeTimes:
    def test_dropped_when_the_output_folder_already_names_the_corpus(self, tmp_path):
        corpus = tmp_path / "harrypotter_r_corpus_10_17_2024"
        out = tmp_path / "corpus_profile_harrypotter_r_corpus_10_17_2024"
        out.mkdir()
        name = os.path.basename(io.generate_output_file_name("", str(corpus), str(out), ".csv", "SVO", "Stanza"))
        assert "harrypotter_r_corpus_10_17_2024" not in name
        assert "SVO" in name and "Stanza" in name  # the labels that identify it still there

    def test_KEPT_when_the_output_folder_does_not(self, tmp_path):
        """A file written somewhere that does not say which corpus it came from must still say so."""
        corpus = tmp_path / "harrypotter_r_corpus_10_17_2024"
        out = tmp_path / "somewhere_else"
        out.mkdir()
        name = os.path.basename(io.generate_output_file_name("", str(corpus), str(out), ".csv", "SVO", "Stanza"))
        assert "Dir_harrypotter_r_corpus_10_17_2024" in name


# ---- formerly tests/test_output_file_name_calls.py ----------------------------------------------------------

import ast  # noqa: E402
import glob  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
KNOWN = {"html_annotator_extractor_util_NEW.py"}  # dead file, deleted by PR #1706


def shifted_calls():
    found = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.py"))):
        if os.path.basename(path) in KNOWN:
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if name != "generate_output_file_name":
                continue
            for slot in (1, 2):  # inputDir, outputDir
                arg = node.args[slot] if len(node.args) > slot else None
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("."):
                    found.append(f"{os.path.basename(path)}:{node.lineno}")
    return found


def test_no_extension_in_a_folder_argument():
    assert shifted_calls() == []
