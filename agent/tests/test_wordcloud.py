import importlib.util
import io
import os
from collections import defaultdict

import pytest

pytest.importorskip("wordcloud")

from wordclouds_util import (
    GroupedColorFunc,
    display_wordCloud,
    get_font_path,
    get_wordcloud_title,
    processColorList,
    python_wordCloud,
)

RED = "(250, 0, 0)"
GREY = "(169, 169, 169)"


def test_grouped_color_func_maps_words_to_colors():
    color_func = GroupedColorFunc({RED: ["alpha", "beta"]}, GREY)
    assert color_func("alpha") == "rgb(250, 0, 0)"
    assert color_func("beta") == "rgb(250, 0, 0)"
    assert color_func("unknown") == "rgb(169, 169, 169)"


def test_get_font_path_default_and_missing():
    assert get_font_path("Default") is None
    assert get_font_path("") is None
    assert get_font_path(None) is None
    assert get_font_path("no-such-font-xyzzy") is None


def test_get_wordcloud_title():
    assert get_wordcloud_title("/a/b/doc.txt", "", "") == "Wordcloud for doc.txt"
    assert get_wordcloud_title("", "/a/corpus", "") == "Wordcloud for corpus"
    assert get_wordcloud_title("/a/b/doc.txt", "", "My title") == "My title"


def test_process_color_list():
    csv_text = "ColA,ColB\nApple Pie,skip\nBanana,skip\n"
    color_to_words = defaultdict(list)
    # format: field names followed by their color, terminated by '|'
    csv_field_color_list = ["ColA", RED, "|"]
    currenttext, color_to_words = processColorList(
        "", True, color_to_words, csv_field_color_list, io.StringIO(csv_text)
    )
    # words from ColA get a positional '_' suffix tying them to their color
    assert color_to_words[RED] == ["apple_", "pie_", "banana_"]
    assert "apple_ pie_" in currenttext
    # ColB was not selected, so its values are not added
    assert "skip" not in currenttext


def test_display_wordCloud_writes_png(tmp_path):
    text = "research corpus words appear research corpus words research corpus research"
    (tmp_path / "sample.txt").write_text(text, encoding="utf-8")
    output = display_wordCloud(
        str(tmp_path / "sample.txt"),
        "",
        str(tmp_path),
        text,
        doNotListIndividualFiles=True,
        transformed_image_mask=[],
        stopwords="",
        collocation=False,
        wordcloud_title="",
        prefer_horizontal=0.9,
        bg_image=None,
        bg_image_flag=False,
        font=None,
        max_words=50,
    )
    assert output is not None
    assert os.path.isfile(output)
    assert output.endswith(".png")
    assert os.path.getsize(output) > 0


def test_display_wordCloud_empty_text_returns_none(tmp_path):
    assert display_wordCloud("f.txt", "", str(tmp_path), "", True, [], "", False, "", 0.9) is None


def _write_conll_fixture(path):
    # check_CoNLL requires ID, Form, Lemma headers and exactly 13 or 14 columns
    headers = [
        "ID",
        "Form",
        "Lemma",
        "POS",
        "NER",
        "Head",
        "DepRel",
        "Clausal_Tag",
        "Record_ID",
        "Sentence_ID",
        "Document_ID",
        "Document",
        "Misc",
    ]
    rows = [
        ["1", "Dogs", "dog", "NNS"],
        ["2", "chase", "chase", "VBP"],
        ["3", "fast", "fast", "JJ"],
        ["4", "cats", "cat", "NNS"],
        ["5", "quickly", "quickly", "RB"],
        ["6", "dogs", "dog", "NNS"],
    ]
    lines = [",".join(headers)]
    for r in rows:
        lines.append(",".join(r + ["x"] * (len(headers) - len(r))))
    path.write_text("\n".join(lines), encoding="utf-8")


def test_python_wordCloud_conll_csv(tmp_path):
    conll_csv = tmp_path / "conll.csv"
    _write_conll_fixture(conll_csv)
    files = python_wordCloud(
        str(conll_csv),
        "",
        str(tmp_path),
        configFileName="",
        selectedImage="",
        use_contour_only=False,
        wordcloud_title="",
        prefer_horizontal=False,
        font="Default",
        max_words=100,
        lemmatize=False,
        exclude_stopwords=False,
        exclude_punctuation=False,
        lowercase=True,
        differentPOS_differentColors=True,
        differentColumns_differentColors=False,
        csvField_color_list=[],
        doNotListIndividualFiles=True,
        openOutputFiles=False,
        collocation=False,
    )
    assert len(files) == 1
    assert os.path.isfile(files[0])
    assert files[0].endswith(".png")


@pytest.mark.integration
@pytest.mark.skipif(importlib.util.find_spec("stanza") is None, reason="stanza not installed")
def test_python_wordCloud_txt_stanza(tmp_path, fixture_txt):
    files = python_wordCloud(
        str(fixture_txt),
        "",
        str(tmp_path),
        configFileName="",
        selectedImage="",
        use_contour_only=False,
        wordcloud_title="",
        prefer_horizontal=False,
        font="Default",
        max_words=100,
        lemmatize=False,
        exclude_stopwords=True,
        exclude_punctuation=False,
        lowercase=True,
        differentPOS_differentColors=False,
        differentColumns_differentColors=False,
        csvField_color_list=[],
        doNotListIndividualFiles=True,
        openOutputFiles=False,
        collocation=False,
    )
    assert len(files) >= 1
    assert all(os.path.isfile(f) for f in files)
