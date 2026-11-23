"""Stanza pipelines reuse the models already on disk instead of fetching resources.json on every build (#1764).

stanza.Pipeline() defaults to DownloadMethod.DOWNLOAD_RESOURCES: it downloads resources.json from GitHub every time a
pipeline is built, so with no internet every Stanza tool stopped with ConnectionError although its models had been
downloaded. IO_internet_util.stanza_pipeline builds it with DownloadMethod.REUSE_RESOURCES: the local resources.json
and models are used, and only a missing model (or a missing resources.json) is downloaded. Every pipeline in src/ is
built through it. Stanza is stubbed: CI does not install it.
"""

import ast
import enum
import glob
import os
import sys
import types

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
sys.path.insert(0, SRC)

import IO_internet_util as net  # noqa: E402


class _DownloadMethod(enum.Enum):
    NONE = 1
    REUSE_RESOURCES = 2
    DOWNLOAD_RESOURCES = 3


def _fake_stanza(monkeypatch):
    calls = []
    stanza = types.ModuleType("stanza")
    stanza.Pipeline = lambda *args, **kwargs: calls.append((args, kwargs)) or "pipeline"
    core = types.ModuleType("stanza.pipeline.core")
    core.DownloadMethod = _DownloadMethod
    pipeline = types.ModuleType("stanza.pipeline")
    pipeline.core = core
    stanza.pipeline = pipeline
    monkeypatch.setitem(sys.modules, "stanza", stanza)
    monkeypatch.setitem(sys.modules, "stanza.pipeline", pipeline)
    monkeypatch.setitem(sys.modules, "stanza.pipeline.core", core)
    return calls


def test_pipeline_reuses_local_resources(monkeypatch):
    calls = _fake_stanza(monkeypatch)
    assert net.stanza_pipeline(lang="en", processors="tokenize,lemma", verbose=False) == "pipeline"
    (args, kwargs) = calls[0]
    assert kwargs["download_method"] is _DownloadMethod.REUSE_RESOURCES
    assert kwargs["lang"] == "en" and kwargs["processors"] == "tokenize,lemma" and kwargs["verbose"] is False


def test_positional_language_is_passed_through(monkeypatch):
    calls = _fake_stanza(monkeypatch)
    net.stanza_pipeline("fr", processors="tokenize")
    assert calls[0][0] == ("fr",)


def test_an_explicit_download_method_is_kept(monkeypatch):
    calls = _fake_stanza(monkeypatch)
    net.stanza_pipeline(lang="en", download_method=_DownloadMethod.DOWNLOAD_RESOURCES)
    assert calls[0][1]["download_method"] is _DownloadMethod.DOWNLOAD_RESOURCES


def test_no_pipeline_in_src_is_built_with_stanza_pipeline_directly():
    direct = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.py"))):
        if os.path.basename(path) == "IO_internet_util.py":
            continue
        for n in ast.walk(ast.parse(open(path, encoding="utf-8-sig").read())):
            if (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "Pipeline"
                and isinstance(n.func.value, ast.Name)
                and n.func.value.id == "stanza"
            ):
                direct.append(f"{os.path.basename(path)}:{n.lineno}")
    assert direct == [], "build Stanza pipelines with IO_internet_util.stanza_pipeline: " + ", ".join(direct)


def test_multilingual_pipeline_reuses_local_resources(monkeypatch):
    _fake_stanza(monkeypatch)
    calls = []
    multilingual = types.ModuleType("stanza.pipeline.multilingual")
    multilingual.MultilingualPipeline = lambda *args, **kwargs: calls.append(kwargs) or "multilingual"
    monkeypatch.setitem(sys.modules, "stanza.pipeline.multilingual", multilingual)
    assert net.stanza_multilingual_pipeline(lang_id_config={"langid_lang_subset": ["en"]}) == "multilingual"
    assert calls[0]["download_method"] is _DownloadMethod.REUSE_RESOURCES
    assert calls[0]["lang_id_config"] == {"langid_lang_subset": ["en"]}


def test_no_multilingual_pipeline_in_src_is_built_directly():
    direct = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.py"))):
        if os.path.basename(path) == "IO_internet_util.py":
            continue
        for n in ast.walk(ast.parse(open(path, encoding="utf-8-sig").read())):
            if (
                isinstance(n, ast.Call)
                and getattr(n.func, "id", getattr(n.func, "attr", None)) == "MultilingualPipeline"
            ):
                direct.append(f"{os.path.basename(path)}:{n.lineno}")
    assert direct == [], "build it with IO_internet_util.stanza_multilingual_pipeline: " + ", ".join(direct)
