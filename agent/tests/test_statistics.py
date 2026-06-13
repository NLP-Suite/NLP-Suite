import pytest
from conftest import output_csvs, read_rows

# statistics_txt_main pulls in the chart/stanza stack at call time; the module
# itself only needs core utils, but skip on hosts without the agent image deps.
try:
    import statistics_txt_util
    from statistics_txt_main import run_statistics
except (ImportError, SystemExit):
    pytest.skip("statistics dependencies not available", allow_module_level=True)


def _run(tiny_corpus, tmp_output, **kwargs):
    args = dict(
        inputFilename="",
        inputDir=str(tiny_corpus),
        outputDir=str(tmp_output),
        corpus_statistics_options_menu_var="",
        corpus_text_options_menu_var="none",
        openOutputFiles=False,
        chartPackage="No charts",
        dataTransformation="No transformation",
        corpus_statistics_var=False,
        corpus_statistics_byPOS_var=False,
    )
    args.update(kwargs)
    return run_statistics(**args)


def test_no_options_selected_returns_none(tiny_corpus, tmp_output):
    assert _run(tiny_corpus, tmp_output) is None
    assert output_csvs(tmp_output) == []


def test_line_length(tiny_corpus, tmp_output):
    _run(
        tiny_corpus,
        tmp_output,
        corpus_statistics_var=True,
        corpus_statistics_options_menu_var="Compute line length",
    )
    csvs = [f for f in output_csvs(tmp_output) if "line_length" in f]
    assert len(csvs) == 1
    rows = read_rows(csvs[0])
    assert len(rows) >= 8  # at least one line per fixture document
    assert all(int(r["Line length (in words)"]) > 0 for r in rows)
    assert {int(r["Document ID"]) for r in rows} == set(range(1, 9))


def test_sentence_length(tiny_corpus, tmp_output):
    _run(
        tiny_corpus,
        tmp_output,
        corpus_statistics_var=True,
        corpus_statistics_options_menu_var="Compute sentence length",
    )
    csvs = [f for f in output_csvs(tmp_output) if "sentence_length" in f]
    assert len(csvs) == 1
    rows = read_rows(csvs[0])
    assert len(rows) >= 8  # at least one sentence per fixture document
    assert all(int(r["Sentence length (in words)"]) > 0 for r in rows)
    assert {int(r["Document ID"]) for r in rows} == set(range(1, 9))


def test_corpus_frequencies(tiny_corpus, tmp_output):
    # corpus_text_options_menu_var='none' skips the (very slow) per-word
    # stanza lemmatization and the stopword filter
    _run(
        tiny_corpus,
        tmp_output,
        corpus_statistics_var=True,
        corpus_statistics_options_menu_var="frequencies",
    )
    csvs = [f for f in output_csvs(tmp_output) if "corpus_stats" in f]
    assert csvs, "expected a corpus_stats csv in a corpus_stats subdirectory"
    rows = read_rows(csvs[0])
    assert len(rows) == 8  # one row per fixture document
    for r in rows:
        assert int(r["Number of documents in corpus"]) == 8
        assert int(r["Number of Words in Document"]) > 0
        assert r["Word1"] != ""
        assert int(r["Frequency1"]) >= 1


def test_by_pos_stanza(tiny_corpus, tmp_output):
    # exercises the Stanza POS annotator path; hermetic (models baked into
    # the agent image) but slow
    _run(tiny_corpus, tmp_output, corpus_statistics_byPOS_var=True)
    csvs = output_csvs(tmp_output)
    assert csvs, "expected Stanza POS output csv(s)"


# ---------------------------------------------------------------------------
# pure helpers


def test_word_count():
    counts = statistics_txt_util.word_count("the cat saw the dog")
    assert counts == {"the": 2, "cat": 1, "saw": 1, "dog": 1}


def test_tokenize():
    assert statistics_txt_util.tokenize("it's a fine-day today") == [
        "it's",
        "a",
        "fine-day",
        "today",
    ]


def test_get_yules_k_i():
    # needs repeated tokens: all-distinct tokens make m2 == m1 and divide by zero
    k, i = statistics_txt_util.get_yules_k_i("the cat and the dog and the bird")
    assert k > 0
    assert i > 0


def test_no_txt_files_writes_no_rows(tmp_path, tmp_output):
    # empty input dir: line length writes a header-only csv, no data rows
    empty = tmp_path / "empty_input"
    empty.mkdir()
    _run(
        empty,
        tmp_output,
        corpus_statistics_var=True,
        corpus_statistics_options_menu_var="Compute line length",
    )
    for f in output_csvs(tmp_output):
        assert read_rows(f) == []
