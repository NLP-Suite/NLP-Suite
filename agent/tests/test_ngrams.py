import pathlib

import pytest

try:
    from NGrams_CoOccurrences import run_ngrams
except (ImportError, SystemExit):
    pytest.skip("NGrams_CoOccurrences dependencies not available", allow_module_level=True)


def _run(tiny_corpus, tmp_output, **kwargs):
    args = dict(
        inputFilename="",
        inputDir=str(tiny_corpus),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="No charts",
        dataTransformation="No transformation",
        ngrams_options_list=[],
        Ngrams_compute_var=False,
        ngrams_menu_var="",
        ngrams_options_menu_var="",
        ngrams_size=2,
        search_words="",
        minus_K_words_var=0,
        plus_K_words_var=0,
        Ngrams_search_var=False,
        csv_file_var="",
        ngrams_viewer_var=False,
        CoOcc_Viewer_var=False,
        date_options=False,
        temporal_aggregation_var="",
        viewer_options_list=[],
        language_list=["English"],
        config_input_output_numeric_options=[1, 0, 0, 1],
        number_of_years=0,
    )
    args.update(kwargs)
    return run_ngrams(**args)


def test_no_options_selected_returns_none(tiny_corpus, tmp_output):
    assert _run(tiny_corpus, tmp_output) is None
    assert list(pathlib.Path(tmp_output).iterdir()) == []


def test_csv_file_reminder_aborts(tiny_corpus, tmp_output):
    assert _run(tiny_corpus, tmp_output, csv_file_var="some.csv", Ngrams_compute_var=True) is None
    assert list(pathlib.Path(tmp_output).iterdir()) == []


def test_unavailable_postag_option_aborts(tiny_corpus, tmp_output):
    files = _run(
        tiny_corpus,
        tmp_output,
        Ngrams_compute_var=True,
        ngrams_menu_var="Word",
        ngrams_options_list=["POSTAG"],
    )
    assert files is None
    assert list(pathlib.Path(tmp_output).rglob("*.csv")) == []


def test_compute_word_bigrams(tiny_corpus, tmp_output):
    files = _run(
        tiny_corpus,
        tmp_output,
        Ngrams_compute_var=True,
        ngrams_menu_var="Word",
        ngrams_size=2,
    )
    csvs = list(pathlib.Path(tmp_output).rglob("*.csv"))
    assert csvs, "expected n-gram csv outputs"
    assert files, "compute-only runs should return the produced files"
    existing = [f for f in files if isinstance(f, str) and f]
    assert existing and all(pathlib.Path(f).exists() for f in existing)
