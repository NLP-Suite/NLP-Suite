import os

import pytest
from conftest import output_csvs as _output_csvs
from conftest import read_rows as _read_rows

# sentiment_analysis imports pandas-dependent helpers at module level; skip on
# hosts without the agent image's dependencies.
try:
    from sentiment_analysis import run_sentiment_analysis
except (ImportError, SystemExit):
    pytest.skip("sentiment_analysis dependencies not available", allow_module_level=True)


def _run(tiny_corpus, tmp_output, algorithm, mean_var=True, median_var=False):
    run_sentiment_analysis(
        inputDir=str(tiny_corpus),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="No charts",
        dataTransformation="No transformation",
        mean_var=mean_var,
        median_var=median_var,
        SA_algorithm_var=algorithm,
    )


def test_no_algorithm_selected_writes_nothing(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, "")
    assert _output_csvs(tmp_output) == []


def test_unknown_algorithm_writes_nothing(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, "no-such-algorithm")
    assert _output_csvs(tmp_output) == []


def test_vader(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, "VADER")
    csvs = [f for f in _output_csvs(tmp_output) if "VADER" in f]
    assert len(csvs) == 1
    rows = _read_rows(csvs[0])
    assert len(rows) >= 8  # at least one sentence row per fixture document
    assert all(-1.0 <= float(r["Sentiment score"]) <= 1.0 for r in rows)
    assert {r["Sentiment label"] for r in rows} <= {"positive", "negative", "neutral"}
    # doc01 contains clearly positive sentences ("delicious", "loved", "wonderful")
    doc01 = [r for r in rows if "doc01" in r["Document"]]
    assert any(r["Sentiment label"] == "positive" for r in doc01)
    # documents are numbered in order
    assert {int(r["Document ID"]) for r in rows} == set(range(1, 9))


def test_vader_defaults_mean_when_neither_ticked(tiny_corpus, tmp_output):
    # neither mean nor median ticked used to silently skip every algorithm
    _run(tiny_corpus, tmp_output, "VADER", mean_var=False, median_var=False)
    assert len([f for f in _output_csvs(tmp_output) if "VADER" in f]) == 1


def test_hedonometer_both_modes(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, "hedonometer", mean_var=True, median_var=True)
    csvs = [f for f in _output_csvs(tmp_output) if "Hedo" in f]
    assert len(csvs) == 1
    rows = _read_rows(csvs[0])
    assert len(rows) >= 8
    scored = [r for r in rows if r["Word List"]]
    assert scored, "expected at least one sentence with hedonometer words"
    for r in scored:
        assert 1.0 <= float(r["Sentiment score (Mean)"]) <= 9.0
        assert 1.0 <= float(r["Sentiment score (Median)"]) <= 9.0


def test_anew(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, "ANEW")
    csvs = [f for f in _output_csvs(tmp_output) if "ANEW" in f]
    assert len(csvs) == 1
    rows = _read_rows(csvs[0])
    assert rows, "expected at least one sentence with ANEW words"
    for r in rows:
        assert 1.0 <= float(r["Sentiment score (Mean)"]) <= 9.0
        assert r["Sentiment label (Mean)"] != ""
    # sentence IDs increment within a document (regression: IDs were stuck at 1)
    doc_ids = [int(r["Sentence ID"]) for r in rows if "doc01" in r["Document"]]
    assert doc_ids == sorted(doc_ids)


def test_sentiwordnet(tiny_corpus, tmp_output):
    # downloads nltk corpora (wordnet, sentiwordnet, ...) on first run
    _run(tiny_corpus, tmp_output, "SentiWordNet")
    csvs = [f for f in _output_csvs(tmp_output) if "SentiWordNet" in f]
    assert len(csvs) == 1
    rows = _read_rows(csvs[0])
    assert len(rows) >= 8
    assert {r["Sentiment label"] for r in rows} <= {"positive", "negative", "neutral"}


@pytest.mark.skipif(
    not os.environ.get("NLP_SUITE_TEST_BERT"),
    reason="downloads a ~500MB HuggingFace model; set NLP_SUITE_TEST_BERT=1 to run",
)
def test_bert(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, "BERT")
    csvs = [f for f in _output_csvs(tmp_output) if "roBERTa" in f]
    assert len(csvs) == 1
    rows = _read_rows(csvs[0])
    assert len(rows) >= 8
    assert all(0.0 <= float(r["Sentiment score"]) <= 1.0 for r in rows)
