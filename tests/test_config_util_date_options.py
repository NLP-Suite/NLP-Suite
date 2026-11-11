"""get_date_options must not crash when there is no I/O config file yet (a first run).

With no config file, read_config_file returns template rows of five fields, [label, "", "", "", 0];
a saved config has six (label, path, sort order, separator, date format, date position). The date
check read row[4] (the integer 0 in a template row, never equal to "") as a date format and then
row[5], so Sample corpus crashed at open with IndexError on a first run from source.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# conftest stubs config_util (it is infra for other modules under test); this file tests the real one.
sys.modules.pop("config_util", None)
import config_util  # noqa: E402

CONFIG = "NLP_default_IO_config.csv"
NUMERIC = [0, 1, 0, 1]  # input dir + output dir, as Sample corpus asks
DEFAULTS = (0, "mm/dd/yyyy", "_", 2)


def _use_config_dir(monkeypatch, path):
    monkeypatch.setattr(config_util.GUI_IO_util, "configPath", str(path), raising=False)
    monkeypatch.setattr(config_util.GUI_IO_util, "NLPPath", str(path), raising=False)


def _write_config(path, input_dir_row):
    rows = [
        "I/O File type,Path,Sort order,Date separator,Date format,Date position",
        "Input txt filename with path,,,,,",
        input_dir_row,
        "Input files secondary directory,,,,,",
        "Output files directory,/out,,,,",
    ]
    (path / CONFIG).write_text("\n".join(rows) + "\n", encoding="utf-8")


class TestGetDateOptions:
    def test_no_config_file_gives_the_defaults(self, tmp_path, monkeypatch):
        _use_config_dir(monkeypatch, tmp_path)
        result = config_util.get_date_options(CONFIG, NUMERIC)
        assert result == DEFAULTS + (False,)

    def test_a_saved_config_with_a_date_is_read(self, tmp_path, monkeypatch):
        _use_config_dir(monkeypatch, tmp_path)
        _write_config(tmp_path, "Input files directory,/corpus,0,-,dd-mm-yyyy,3")
        result = config_util.get_date_options(CONFIG, NUMERIC)
        assert result == (1, "dd-mm-yyyy", "-", 3, True)

    def test_a_saved_config_without_a_date_gives_the_defaults(self, tmp_path, monkeypatch):
        _use_config_dir(monkeypatch, tmp_path)
        _write_config(tmp_path, "Input files directory,/corpus,0,,,")
        result = config_util.get_date_options(CONFIG, NUMERIC)
        assert result == DEFAULTS + (True,)
