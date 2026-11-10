"""Tests for the model-download failure reporting.

The behaviour under test is what an inexperienced user sees when a language model cannot be
downloaded: previously a ConnectionError reached the terminal only and the process exited, so someone
running the Suite from the app saw the window vanish with no explanation.
"""

import ast
import os
import sys
import threading
import time
import types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

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
    monkeypatch.setattr(net, "mb", rec)
    monkeypatch.setattr(net, "internet_on", lambda: False)
    return rec


def _module(name, **attrs):
    """A stand-in module with the given attributes."""
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


def _boom():
    raise ConnectionError("getaddrinfo failed")


class TestDownloadWithWarning:
    def test_success_is_silent(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, "mb", rec)
        monkeypatch.setattr(net, "internet_on", lambda: True)
        assert net.download_with_warning("x", lambda: None) is True
        assert rec.errors == []

    def test_retries_once_when_the_user_bypasses_the_check(self, monkeypatch):
        _offline(monkeypatch, answer=True)
        calls = []

        def fn():
            calls.append(1)
            raise ConnectionError("getaddrinfo failed")

        net.download_with_warning("x", fn)
        # the old code offered the bypass but never tried again, so answering Yes changed nothing
        assert len(calls) == 2

    def test_retry_can_succeed(self, monkeypatch):
        _offline(monkeypatch, answer=True)
        state = {"n": 0}

        def fn():
            state["n"] += 1
            if state["n"] == 1:
                raise ConnectionError("transient")

        assert net.download_with_warning("x", fn) is True

    def test_reports_failure_and_returns_false(self, monkeypatch):
        rec = _offline(monkeypatch, answer=True)
        assert net.download_with_warning("x", _boom) is False
        assert len(rec.errors) == 1

    def test_declining_the_bypass_still_reports(self, monkeypatch):
        rec = _offline(monkeypatch, answer=False)
        assert net.download_with_warning("x", _boom) is False
        assert len(rec.errors) == 1

    def test_only_one_dialog_beyond_the_yes_no_question(self, monkeypatch):
        rec = _offline(monkeypatch, answer=True)
        net.download_with_warning("x", _boom)
        assert len(rec.errors) == 1


def _model_folder(tmp_path, lang="en", files=("tokenize/combined.pt",)):
    """A Stanza-like resources folder under tmp_path; returns the resources root."""
    for rel in files:
        target = tmp_path / lang / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x")
    return str(tmp_path)


class TestStanzaModelPresent:
    """Opening a GUI must not re-check a model that is already on disk (9-11 s per check)."""

    def test_present_when_the_tokenizer_model_is_there(self, tmp_path):
        assert net.stanza_model_present("en", resources_dir=_model_folder(tmp_path)) is True

    def test_absent_when_the_folder_is_missing(self, tmp_path):
        assert net.stanza_model_present("en", resources_dir=str(tmp_path)) is False

    def test_absent_for_another_language(self, tmp_path):
        assert net.stanza_model_present("it", resources_dir=_model_folder(tmp_path, "en")) is False

    def test_an_interrupted_download_is_not_a_model(self, tmp_path):
        # the first download writes default.zip and unpacks it afterwards
        root = _model_folder(tmp_path, files=("default.zip",))
        assert net.stanza_model_present("en", resources_dir=root) is False

    def test_an_empty_tokenize_folder_is_not_a_model(self, tmp_path):
        (tmp_path / "en" / "tokenize").mkdir(parents=True)
        assert net.stanza_model_present("en", resources_dir=str(tmp_path)) is False

    def test_looks_where_stanza_itself_keeps_models(self, tmp_path, monkeypatch):
        # Stanza 1.10+ keeps models in a per-version cache folder (e.g. ~/Library/Caches/stanza/1.14.0/resources
        # on Mac, %LOCALAPPDATA%\StanfordNLP\stanza\Cache\<version>\resources on Windows), not in
        # ~/stanza_resources. Checking the old folder made every import re-download (issue #1703).
        root = _model_folder(tmp_path)
        fake = _module("stanza.resources.common", DEFAULT_MODEL_DIR=root)
        monkeypatch.setitem(sys.modules, "stanza.resources", types.ModuleType("stanza.resources"))
        monkeypatch.setitem(sys.modules, "stanza.resources.common", fake)
        assert net.stanza_resources_dir() == root
        assert net.stanza_model_present("en") is True


class TestEnsureStanzaModel:
    def test_no_download_when_the_model_is_on_disk(self, tmp_path):
        calls = []
        ok = net.ensure_stanza_model("x", lambda: calls.append(1), resources_dir=_model_folder(tmp_path))
        assert ok is True
        assert calls == []

    def test_downloads_when_the_model_is_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(net, "mb", _Recorder())
        calls = []
        ok = net.ensure_stanza_model("x", lambda: calls.append(1), resources_dir=str(tmp_path))
        assert ok is True
        assert calls == [1]

    def test_a_failed_download_is_reported_not_swallowed(self, tmp_path, monkeypatch):
        rec = _offline(monkeypatch, answer=False)
        assert net.ensure_stanza_model("x", _boom, resources_dir=str(tmp_path)) is False
        assert len(rec.errors) == 1

    def test_the_default_download_fetches_the_requested_language(self, tmp_path, monkeypatch):
        monkeypatch.setattr(net, "mb", _Recorder())
        calls = []
        fake = _module("stanza", download=lambda lang, model_dir=None: calls.append((lang, model_dir)))
        monkeypatch.setitem(sys.modules, "stanza", fake)
        assert net.ensure_stanza_model("x", lang="it", resources_dir=str(tmp_path)) is True
        assert calls == [("it", str(tmp_path))]

    def test_the_download_does_not_run_on_the_calling_thread(self, tmp_path, monkeypatch):
        # the calling thread is the Tk thread: blocking it is what froze the GUI (issue #1703)
        monkeypatch.setattr(net, "mb", _Recorder())
        threads = []
        net.ensure_stanza_model("x", lambda: threads.append(threading.current_thread()), resources_dir=str(tmp_path))
        assert threads and threads[0] is not threading.current_thread()


def _fake_huggingface_hub(monkeypatch, cache="/nowhere"):
    """A stand-in huggingface_hub whose constants the download code reads and changes."""
    constants = _module("huggingface_hub.constants", HF_HUB_DISABLE_XET=False, HF_HUB_CACHE=cache)
    hub = _module("huggingface_hub", constants=constants)
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub)
    monkeypatch.setitem(sys.modules, "huggingface_hub.constants", constants)
    return constants


class TestXetOff:
    """Xet downloads of the Stanza models stalled at 0 bytes on a Mac; plain HTTP finished (issue #1703)."""

    def test_the_stanza_download_runs_with_xet_off_and_restores_it(self, tmp_path, monkeypatch):
        monkeypatch.setattr(net, "mb", _Recorder())
        constants = _fake_huggingface_hub(monkeypatch)
        seen = []
        fake = _module("stanza", download=lambda lang, model_dir=None: seen.append(constants.HF_HUB_DISABLE_XET))
        monkeypatch.setitem(sys.modules, "stanza", fake)
        assert net.ensure_stanza_model("x", resources_dir=str(tmp_path)) is True
        assert seen == [True]
        assert constants.HF_HUB_DISABLE_XET is False  # the rest of the Suite is left as it was

    def test_restored_even_when_the_download_fails(self, monkeypatch):
        constants = _fake_huggingface_hub(monkeypatch)
        try:
            with net.xet_off():
                raise ConnectionError("x")
        except ConnectionError:
            pass
        assert constants.HF_HUB_DISABLE_XET is False

    def test_works_without_huggingface_hub(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "huggingface_hub", None)  # older Stanza downloads without it
        with net.xet_off():
            pass


class TestDownloadProgress:
    """Stanza 1.14 downloads into the Hugging Face cache and copies the files over at the end, so the
    Stanza folder alone showed 0 MB for the whole download."""

    def test_the_huggingface_cache_folder_of_the_language(self, monkeypatch):
        _fake_huggingface_hub(monkeypatch, cache=os.path.join("c", "hub"))
        assert net.huggingface_stanza_cache_dir("my") == os.path.join("c", "hub", "models--stanfordnlp--stanza-my")

    def test_no_cache_folder_without_huggingface_hub(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "huggingface_hub", None)
        assert net.huggingface_stanza_cache_dir("en") is None

    def test_counts_the_first_folder_that_exists(self, tmp_path):
        (tmp_path / "hf").mkdir()
        (tmp_path / "hf" / "blob.incomplete").write_bytes(b"x" * (2 * 1024 * 1024))
        (tmp_path / "stanza").mkdir()
        dirs = [str(tmp_path / "hf"), str(tmp_path / "stanza")]
        assert net.downloaded_mb(dirs) == 2

    def test_falls_back_to_the_stanza_folder(self, tmp_path):
        (tmp_path / "stanza").mkdir()
        (tmp_path / "stanza" / "default.zip").write_bytes(b"x" * (1024 * 1024))
        assert net.downloaded_mb([None, str(tmp_path / "hf"), str(tmp_path / "stanza")]) == 1


class TestRunWithProgress:
    def test_runs_the_work_and_waits_for_it(self):
        done = []
        net.run_with_progress(lambda: (time.sleep(0.05), done.append(1)), poll_seconds=0.01)
        assert done == [1]

    def test_an_error_in_the_work_reaches_the_caller(self):
        try:
            net.run_with_progress(_boom, poll_seconds=0.01)
        except ConnectionError:
            return
        raise AssertionError("the error was swallowed")


class TestDownloadMessage:
    def test_gives_the_real_size_and_says_it_stays_up(self):
        msg = net.stanza_download_message("en")
        assert "about 1 GB" in msg and "525" not in msg
        assert "closes by itself" in msg

    def test_names_the_language(self):
        assert "Italian" in net.stanza_download_message("it", "Italian")


class TestFolderSize:
    def test_counts_every_file_below(self, tmp_path):
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "big.bin").write_bytes(b"x" * (3 * 1024 * 1024))
        assert net.folder_size_mb(str(tmp_path)) == 3

    def test_a_missing_folder_is_zero(self, tmp_path):
        assert net.folder_size_mb(str(tmp_path / "nope")) == 0


def _module_level_calls(path):
    """Names of the functions a module calls when it is imported (outside def/class bodies)."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    names = []

    def visit(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return
        if isinstance(node, ast.Call):
            f = node.func
            names.append(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""))
        for child in ast.iter_child_nodes(node):
            visit(child)

    for stmt in tree.body:
        visit(stmt)
    return names


class TestNoDownloadAtImport:
    """Opening a GUI must not download or re-check a Stanza model (issue #1703)."""

    def test_the_stanza_modules_do_not_download_when_imported(self):
        src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
        for module in ("Stanza_util", "Stanza_functions_util", "statistics_txt_util", "wordclouds_util"):
            calls = _module_level_calls(os.path.join(src, module + ".py"))
            for banned in ("download", "ensure_stanza_model", "Pipeline", "timed_alert"):
                assert banned not in calls, module + " calls " + banned + " at import"


class TestLazyModel:
    """The shared Stanza pipeline is built the first time it is used, not when a GUI opens."""

    def test_nothing_is_built_until_first_use(self):
        built = []
        net.LazyModel(lambda: built.append(1), "x")
        assert built == []

    def test_built_once_and_called_through(self):
        built = []

        def build():
            built.append(1)
            return lambda text: text.upper()

        pipe = net.LazyModel(build, "x")
        assert pipe("a") == "A"
        assert pipe("b") == "B"
        assert built == [1]

    def test_attributes_come_from_the_real_model(self):
        class _Pipe:
            lang = "en"

        assert net.LazyModel(_Pipe, "x").lang == "en"

    def test_a_build_failure_is_shown_and_raised(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, "mb", rec)
        pipe = net.LazyModel(_boom, "Stanza_functions_util.py", "the Stanza English language model")
        try:
            pipe("text")
        except ConnectionError:
            pass
        else:
            raise AssertionError("the failure must not be swallowed")
        assert len(rec.errors) == 1
        assert "Stanza_functions_util.py" in rec.errors[0][1]

    def test_a_failed_build_is_retried_on_the_next_use(self, monkeypatch):
        monkeypatch.setattr(net, "mb", _Recorder())
        state = {"n": 0}

        def build():
            state["n"] += 1
            if state["n"] == 1:
                raise ConnectionError("transient")
            return lambda text: text

        pipe = net.LazyModel(build, "x")
        try:
            pipe("a")
        except ConnectionError:
            pass
        assert pipe("a") == "a"

    def test_a_builder_that_returns_nothing_is_an_error(self, monkeypatch):
        monkeypatch.setattr(net, "mb", _Recorder())
        pipe = net.LazyModel(lambda: None, "x")
        try:
            pipe("a")
        except RuntimeError:
            pass
        else:
            raise AssertionError("a missing model must raise, not return None")


class TestReportDownloadFailure:
    def test_message_carries_the_real_exception(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, "mb", rec)
        net.report_download_failure("Stanza_functions_util.py", ConnectionError("getaddrinfo failed"))
        _, message = rec.errors[0]
        assert "ConnectionError" in message
        assert "getaddrinfo failed" in message

    def test_message_names_the_script_and_says_what_to_do(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, "mb", rec)
        net.report_download_failure("wordclouds_util.py", OSError("nope"), "the Stanza English language model")
        _, message = rec.errors[0]
        assert "wordclouds_util.py" in message
        assert "the Stanza English language model" in message
        assert "WHAT TO DO" in message

    def test_suggests_the_firewall_and_alternative_package_routes(self, monkeypatch):
        rec = _Recorder()
        monkeypatch.setattr(net, "mb", rec)
        net.report_download_failure("x", OSError("nope"))
        _, message = rec.errors[0]
        assert "raw.githubusercontent.com" in message
        assert "spaCy" in message
