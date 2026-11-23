"""Tests for src/file_spell_checker_util.py, one file per module (folded from 2 files, 23 Nov 2026).

From test_spell_checker_calls.py:

Every call in src/ to a file_spell_checker_util function passes arguments its signature accepts (#1762).

The spell checker GUI called nltk_unusual_words with 10 positional arguments (it takes 6 to 8): TypeError, and with
"*" none of the other checkers ran either. The calls are read with ast across src/ and bound to the signatures read
from file_spell_checker_util's source (it imports nltk, stanza, langdetect... which CI does not install).

From test_language_detection_stanza.py:

Language detection uses Stanza's language identifier only, not its full parser (#1724).

MultilingualPipeline() ran tokenize, POS, lemma and both parsers on every document (about a minute each)
to use only doc.lang.
"""

import ast
import glob
import inspect
import os

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
MODULE = "file_spell_checker_util"


def _signatures():
    source = open(os.path.join(SRC, MODULE + ".py"), encoding="utf-8-sig").read()
    signatures = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef):
            node.body = [ast.Pass()]
            node.decorator_list = []
            node.returns = None
            args = node.args
            for a in args.posonlyargs + args.args + args.kwonlyargs:
                a.annotation = None
            # only the shape of the signature matters: defaults may name things the module imports
            args.defaults = [ast.Constant(None) for _ in args.defaults]
            args.kw_defaults = [None if d is None else ast.Constant(None) for d in args.kw_defaults]
            namespace = {}
            exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), "f", "exec"), namespace)
            signatures[node.name] = inspect.signature(namespace[node.name])
    return signatures


def _calls():
    for path in sorted(glob.glob(os.path.join(SRC, "*.py"))):
        for n in ast.walk(ast.parse(open(path, encoding="utf-8-sig").read())):
            if (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name)
                and n.func.value.id == MODULE
                and not any(isinstance(a, ast.Starred) for a in n.args)
            ):
                yield pytest.param(n, id=f"{os.path.basename(path)}:{n.lineno}:{n.func.attr}")


SIGNATURES = _signatures()


@pytest.mark.parametrize("call", list(_calls()))
def test_call_binds_to_the_signature(call):
    assert call.func.attr in SIGNATURES, f"{MODULE} has no function {call.func.attr}"
    SIGNATURES[call.func.attr].bind(*range(len(call.args)), **{k.arg: None for k in call.keywords if k.arg})


def test_the_spell_checker_gui_calls_nltk_unusual_words():
    assert any("file_spell_checker_main" in p.id and "nltk_unusual_words" in p.id for p in _calls())


# ---- formerly tests/test_language_detection_stanza.py -------------------------------------------------------

import importlib.util  # noqa: E402
import sys  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402

_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "file_spell_checker_util.py")


@pytest.fixture(scope="module")
def fsc():
    # a large module with many third-party imports: stub, while it loads, whatever is missing or stubbed
    stubs = {}
    for name in (
        "spacy",
        "spacy.language",
        "spacy_langdetect",
        "stanza",
        "textblob",
        "autocorrect",
        "fuzzywuzzy",
        "langdetect",
        "langid",
        "langid.langid",
        "spellchecker",
        "pandas",
    ):
        if name not in sys.modules or isinstance(sys.modules[name], MagicMock):
            stubs[name] = MagicMock()
    with patch.dict(sys.modules, stubs):
        for _ in range(30):
            spec = importlib.util.spec_from_file_location("_fsc_langid", _PATH)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                break
            except ModuleNotFoundError as e:
                if not e.name or e.name in sys.modules:
                    raise
                sys.modules[e.name] = MagicMock()
        yield module


# the pipeline is built through IO_internet_util.stanza_pipeline, which reuses local models (#1764)
def test_only_the_langid_processor_is_loaded(fsc):
    with patch.object(fsc, "stanza") as stanza, patch.object(fsc.IO_internet_util, "stanza_pipeline") as build:
        fsc.stanza_langid_pipeline()
    build.assert_called_once_with(lang="multilingual", processors="langid", verbose=False)
    stanza.download.assert_not_called()


def test_the_model_is_downloaded_when_missing(fsc):
    with patch.object(fsc, "stanza") as stanza, patch.object(fsc.IO_internet_util, "stanza_pipeline") as build:
        build.side_effect = [FileNotFoundError("no model"), MagicMock()]
        fsc.stanza_langid_pipeline()
    stanza.download.assert_called_once_with(lang="multilingual", verbose=False)
    assert build.call_count == 2
