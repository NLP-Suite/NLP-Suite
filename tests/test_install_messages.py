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


def test_punkt_also_checks_punkt_tab(iolib):
    # NLTK 3.9+ tokenizers look only for punkt_tab (#1718)
    pairs = iolib.nltk_resources_to_check("tokenizers/punkt", "punkt")
    assert ("tokenizers/punkt", "punkt") in pairs
    assert ("tokenizers/punkt_tab", "punkt_tab") in pairs


def test_the_pos_tagger_also_checks_its_english_json(iolib):
    # NLTK 3.9+ PerceptronTagger loads taggers/averaged_perceptron_tagger_eng/ (SentiWordNet, nominalization)
    pairs = iolib.nltk_resources_to_check("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger")
    assert ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng") in pairs


def test_other_resources_are_checked_alone(iolib):
    assert iolib.nltk_resources_to_check("corpora/wordnet", "wordnet") == [("corpora/wordnet", "wordnet")]


def test_a_missing_punkt_tab_is_downloaded(iolib):
    fake_nltk = mock.MagicMock()

    def find(path):
        if "punkt_tab" in path:
            raise LookupError(path)

    fake_nltk.data.find.side_effect = find
    with (
        mock.patch.dict(sys.modules, {"nltk": fake_nltk, "nltk.data": fake_nltk.data}),
        mock.patch.object(iolib, "IO_user_interface_util"),
    ):
        iolib.import_nltk_resource(None, "tokenizers/punkt", "punkt")
    fake_nltk.download.assert_called_once_with("punkt_tab")


class TestDownloadedBuild:
    """Tools in the zip run on python-env (sys.frozen False): messages must still give zip advice, not conda."""

    def test_tool_on_python_env_is_the_download(self, iolib, tmp_path):
        (tmp_path / "python-env").mkdir()
        assert iolib.downloaded_build(str(tmp_path), frozen=False)

    def test_frozen_menu_is_the_download(self, iolib, tmp_path):
        assert iolib.downloaded_build(str(tmp_path), frozen=True)

    def test_source_checkout(self, iolib, tmp_path):
        (tmp_path / ".git").mkdir()
        (tmp_path / "python-env").mkdir()
        assert not iolib.downloaded_build(str(tmp_path), frozen=False)

    def test_plain_source_folder(self, iolib, tmp_path):
        assert not iolib.downloaded_build(str(tmp_path), frozen=False)
