"""Tests for src/file_converter_util.py, one file per module (folded from 2 files, 23 Nov 2026).

From test_rtf_converter.py:

rtf -> txt converter writes the txt file in the output folder and says what it did (#1766).

For a single input file (no input folder), rtf_converter named the output os.path.join(outputDir,
os.path.relpath(doc, os.path.commonprefix([doc, ""]))): commonprefix with "" is "", so relpath worked relative to
the current directory, and the txt went to outputDir/../../<the input file's path>, outside the output folder, with
no message. The function is pulled out of file_converter_util (which imports pdfminer, docx, striprtf: not in CI)
and run with striprtf's rtf_to_text stubbed.

From test_csv_converter_not_offered.py:

File checker/converter/cleaner: the unfinished csv -> txt converter is not offered (#1768).

file_converter_util.csv_converter answers every csv with "The function is still under construction. Sorry!", yet
"Document converter (csv --> txt)" was the first item of the Convert Files menu. It is out of the menu and of the
option -> function map until it exists.
"""

import ast
import errno
import os
from unittest.mock import MagicMock

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")

RTF = r"""{\rtf1\ansi\ansicpg1252\cocoartf2870
{\fonttbl\f0\fswiss\fcharset0 Helvetica-Light;}
\f0\fs24 \cf0 The book was long.\
It rained.}"""


def _rtf_converter(rtf_to_text=lambda rtf: "The book was long.\nIt rained.\n"):
    source = open(os.path.join(SRC, "file_converter_util.py"), encoding="utf-8").read()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "rtf_converter")
    namespace = {
        "os": os,
        "errno": errno,
        "tk": MagicMock(),
        "mb": MagicMock(),
        "IO_files_util": MagicMock(),
        "IO_user_interface_util": MagicMock(),
        "GUI_util": MagicMock(),
        "rtf_to_text": rtf_to_text,
    }
    exec(ast.get_source_segment(source, node), namespace)
    return namespace["rtf_converter"], namespace


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    (tmp_path / "in").mkdir()
    (tmp_path / "out").mkdir()
    (tmp_path / "elsewhere").mkdir()
    rtf = tmp_path / "in" / "article.rtf"
    rtf.write_text(RTF, encoding="utf-8")
    monkeypatch.chdir(tmp_path / "elsewhere")  # the app's folder, not the input's
    return tmp_path, rtf


def test_single_rtf_file_is_converted_into_the_output_folder(corpus):
    tmp_path, rtf = corpus
    rtf_converter, namespace = _rtf_converter()
    rtf_converter(MagicMock(), str(rtf), "", str(tmp_path / "out"), "cfg.csv", False, "Excel", "No transformation")
    txt = tmp_path / "out" / "article.txt"
    assert txt.read_text(encoding="utf-8") == "The book was long.\nIt rained.\n"
    assert [p.name for p in tmp_path.rglob("*.txt")] == ["article.txt"]


def test_rtf_folder_keeps_subfolders_under_the_output_folder(tmp_path, monkeypatch):
    (tmp_path / "in" / "sub").mkdir(parents=True)
    (tmp_path / "out").mkdir()
    (tmp_path / "in" / "sub" / "a.rtf").write_text(RTF, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    rtf_converter, namespace = _rtf_converter()
    namespace["tk"].messagebox.askyesnocancel.return_value = True
    namespace["IO_files_util"].getFileList_SubDir.return_value = [str(tmp_path / "in" / "sub" / "a.rtf")]
    rtf_converter(MagicMock(), "", str(tmp_path / "in"), str(tmp_path / "out"), "cfg.csv", False, "", "")
    assert (tmp_path / "out" / "sub" / "a.txt").exists()


def test_an_rtf_with_no_text_is_reported(corpus):
    tmp_path, rtf = corpus
    rtf_converter, namespace = _rtf_converter(rtf_to_text=lambda rtf: "  \n")
    rtf_converter(MagicMock(), str(rtf), "", str(tmp_path / "out"), "cfg.csv", False, "Excel", "No transformation")
    assert namespace["mb"].showwarning.call_count == 1
    assert "article.rtf" in str(namespace["mb"].showwarning.call_args)


def test_an_unreadable_rtf_is_reported(corpus):
    tmp_path, rtf = corpus

    def broken(rtf):
        raise ValueError("bad rtf")

    rtf_converter, namespace = _rtf_converter(rtf_to_text=broken)
    rtf_converter(MagicMock(), str(rtf), "", str(tmp_path / "out"), "cfg.csv", False, "Excel", "No transformation")
    assert namespace["mb"].showwarning.call_count == 1
    assert "bad rtf" in str(namespace["mb"].showwarning.call_args)


# ---- formerly tests/test_csv_converter_not_offered.py -------------------------------------------------------

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
SOURCE = open(os.path.join(SRC, "file_checker_converter_cleaner_main.py"), encoding="utf-8").read()


def _convert_menu_values():
    for n in ast.walk(ast.parse(SOURCE)):
        if (
            isinstance(n, ast.Call)
            and getattr(n.func, "attr", None) == "OptionMenu"
            and any(isinstance(a, ast.Name) and a.id == "convert_tools_var" for a in n.args)
        ):
            return [a.value for a in n.args if isinstance(a, ast.Constant)]
    raise AssertionError("Convert Files menu not found")


def test_csv_converter_is_not_in_the_convert_menu():
    values = _convert_menu_values()
    assert "Document converter (docx --> txt)" in values
    assert not any("csv" in v for v in values)


def test_csv_converter_is_not_mapped():
    assert "csv_converter" not in SOURCE
