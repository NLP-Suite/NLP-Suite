"""An output subfolder is made even when the output folder itself does not exist yet.

The zip's default config (lib/config_defaults) sends output to NLP_output inside the NLP Suite folder,
but nothing creates that folder. make_output_subdirectory and make_directory chmod-ed the parent and
then os.mkdir-ed the subfolder, so on a fresh install the first RUN of almost every tool stopped with
"Could not create the directory .../NLP_output/<label>_<input> [Errno 2] No such file or directory".
"""

import importlib.util
import os
import sys

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


io_files = _load()


def test_output_subdirectory_under_a_missing_output_folder(tmp_path):
    output_dir = tmp_path / "NLP_output"  # not created, as on a fresh install
    sub = io_files.make_output_subdirectory("", str(tmp_path / "newspaperArticles"), str(output_dir), "Lemma_Stanza")
    assert sub == str(output_dir / "Lemma_Stanza_newspaperArticles")
    assert os.path.isdir(sub)


def test_output_subdirectory_under_an_existing_output_folder(tmp_path):
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    sub = io_files.make_output_subdirectory("", str(tmp_path / "corpus"), str(output_dir), "NER")
    assert sub == str(output_dir / "NER_corpus")
    assert os.path.isdir(sub)


def test_make_directory_under_a_missing_parent(tmp_path):
    target = tmp_path / "missing" / "new"
    assert io_files.make_directory(str(target)) == str(target)
    assert os.path.isdir(target)
