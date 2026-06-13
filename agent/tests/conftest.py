import csv
import os
import pathlib
import shutil
import socket
import sys
import urllib.parse

import pytest

# Make agent/src importable when running pytest from agent/
_src = pathlib.Path(__file__).parent.parent / "src"
sys.path.insert(0, str(_src))
for _d in _src.iterdir():
    if _d.is_dir() and not _d.name.startswith("."):
        sys.path.insert(0, str(_d))

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def output_csvs(outputDir):
    """All csv files under outputDir (recursive), sorted."""
    return sorted(str(p) for p in pathlib.Path(outputDir).rglob("*.csv"))


def read_rows(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture
def fixture_txt():
    return _FIXTURES / "sample.txt"


@pytest.fixture
def fixture_csv():
    return _FIXTURES / "sample.csv"


@pytest.fixture
def fixture_conll():
    """CoreNLP-format CoNLL table (13 columns; see Stanford_CoreNLP_util)."""
    return _FIXTURES / "sample_conll.csv"


@pytest.fixture
def fixture_locations_csv():
    return _FIXTURES / "locations.csv"


@pytest.fixture
def locations_txt():
    """Directory with one txt doc naming real locations (Rome, Paris)."""
    return _FIXTURES / "locations_txt"


@pytest.fixture
def tiny_corpus():
    """Directory of 8 short txt files (cooking and space themes)."""
    return _FIXTURES / "tiny_corpus"


@pytest.fixture
def tmp_output(tmp_path):
    return tmp_path


@pytest.fixture
def conll_input_dir(tmp_path):
    """Fresh dir holding a copy of sample_conll.csv.

    The CoNLL analyzer scans its input *directory* for the first csv, and
    compute_sentence_table writes next to the input file, so each test gets
    a disposable copy.
    """
    input_dir = tmp_path / "conll_input"
    input_dir.mkdir()
    shutil.copy(_FIXTURES / "sample_conll.csv", input_dir / "sample_conll.csv")
    return input_dir


def _corenlp_hostport():
    url = os.environ.get("CORENLP_URL", "http://localhost:9000")
    parsed = urllib.parse.urlparse(url)
    return parsed.hostname or "localhost", parsed.port or 9000


def _corenlp_up():
    try:
        with socket.create_connection(_corenlp_hostport(), timeout=2):
            return True
    except OSError:
        return False


@pytest.fixture
def corenlp_running():
    if not _corenlp_up():
        host, port = _corenlp_hostport()
        pytest.skip(f"CoreNLP service not available on {host}:{port}")
