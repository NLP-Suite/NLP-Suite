"""The missing-module and NLTK-download messages must fit how the NLP Suite is installed today.

Users run a zip that bundles Python and every package: they have no Anaconda, no STEP1/2/3 scripts and
cannot pip install. Only a source checkout can, and it installs from requirements.txt.
"""

import importlib.util
import os
import sys
from unittest import mock

import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


@pytest.fixture(scope="module")
def iolib():
    # conftest replaces IO_libraries_util with a stub; load the real file under another name
    path = os.path.join(_SRC, "IO_libraries_util.py")
    # CI installs only pytest: stub whatever third-party module the file imports and CI lacks (psutil,
    # requests, ...). The two functions under test are pure string builders and use none of them.
    stubbed = []
    try:
        for _ in range(30):
            spec = importlib.util.spec_from_file_location("IO_libraries_util_real", path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                break
            except ModuleNotFoundError as e:
                if not e.name or e.name in stubbed:
                    raise
                sys.modules[e.name] = mock.MagicMock()
                stubbed.append(e.name)
        else:
            raise RuntimeError("could not load IO_libraries_util.py; stubbed: " + ", ".join(stubbed))
        yield module
    finally:
        for name in stubbed:
            sys.modules.pop(name, None)


def test_missing_modules_message_names_the_script_and_the_modules(iolib):
    msg = iolib.missing_modules_message("SVO_main.py", ["stanza", "pdfminer.six"])
    assert "SVO_main.py" in msg
    assert "stanza, pdfminer.six" in msg


def test_missing_modules_message_points_to_requirements_not_the_old_install(iolib):
    msg = iolib.missing_modules_message("SVO_main.py", ["stanza"])
    assert "pip install -r requirements.txt" in msg
    assert "releases" in msg  # the way out for someone who is not a developer
    for old in ("STEP", "(base)", "zsh", "TIPS_NLP_Anaconda", "Python=3.7"):
        assert old not in msg


def test_nltk_message_in_the_zip_build_gives_no_commands_to_type(iolib):
    msg = iolib.nltk_download_message("wordnet", frozen=True)
    assert "wordnet" in msg
    for old in ("conda", "pip", "terminal", "STEP", "(base)", "nltk.downloader"):
        assert old not in msg


def test_nltk_message_from_source_gives_the_download_command(iolib):
    msg = iolib.nltk_download_message("wordnet", frozen=False)
    assert "python -m nltk.downloader wordnet" in msg
    assert "STEP" not in msg and "(base)" not in msg
