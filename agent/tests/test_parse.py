import csv

import pytest
from conftest import output_csvs, read_rows

try:
    import spaCy_util
    from parsers_annotators import run_parsers_annotators
except (ImportError, SystemExit):
    pytest.skip("parser dependencies not available", allow_module_level=True)


@pytest.fixture(autouse=True)
def _no_spacy_download(monkeypatch):
    # spaCy_annotate shells out to `spacy download` on every call; the model
    # is preinstalled in the agent image, so skip the download
    monkeypatch.setattr(spaCy_util.subprocess, "check_call", lambda *a, **k: 0)


def _run(tiny_corpus, tmp_output, **kwargs):
    args = dict(
        inputFilename="",
        inputDir=str(tiny_corpus),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="No charts",
        dataTransformation="No transformation",
        manual_Coref=False,
        parser_var=False,
        parser_menu_var="",
        single_quote=False,
        CoNLL_table_analyzer_var=False,
        annotators_var=False,
        annotators_menu_var="",
        package="Stanford CoreNLP",
    )
    args.update(kwargs)
    return run_parsers_annotators(**args)


# error paths ---------------------------------------------------------------


def test_separator_label_annotator_rejected(tiny_corpus, tmp_output):
    with pytest.raises(ValueError, match="invalid"):
        _run(tiny_corpus, tmp_output, annotators_var=True, annotators_menu_var="--------------")


def test_unknown_package_rejected(tiny_corpus, tmp_output):
    with pytest.raises(ValueError, match="not supported"):
        _run(tiny_corpus, tmp_output, package="NoSuchPackage", parser_var=True)


def test_analyzer_without_parser_rejected(tiny_corpus, tmp_output):
    with pytest.raises(ValueError, match="parser first"):
        _run(tiny_corpus, tmp_output, parser_var=0, CoNLL_table_analyzer_var=1)


def test_annotator_flag_without_selection_rejected(tiny_corpus, tmp_output):
    with pytest.raises(ValueError, match="no annotator has been selected"):
        _run(tiny_corpus, tmp_output, annotators_var=True, annotators_menu_var="")


def test_word2vec_annotator_rejected(tiny_corpus, tmp_output):
    with pytest.raises(ValueError, match="not available yet"):
        _run(
            tiny_corpus,
            tmp_output,
            annotators_var=True,
            annotators_menu_var="Word embeddings (Word2Vec)",
        )


def test_stanza_constituency_parser_rejected(tiny_corpus, tmp_output):
    with pytest.raises(ValueError, match="not available in Stanza"):
        _run(
            tiny_corpus,
            tmp_output,
            package="Stanza",
            parser_var=True,
            parser_menu_var="Constituency parser",
        )


# hermetic happy paths (spaCy/Stanza models baked into the agent image) ------


def test_parse_spacy_depparse(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, package="spaCy", parser_var=True)
    csvs = [f for f in output_csvs(tmp_output) if "CoNLL_SpaCy" in f]
    assert len(csvs) == 1
    assert "depparse_spaCy" in csvs[0]
    rows = read_rows(csvs[0])
    assert len(rows) >= 8  # tokens from all 8 fixture documents
    for col in ("ID", "Form", "Lemma", "POS", "Head", "DepRel"):
        assert col in rows[0]
    # note: spaCy's table is NOT the 13-column CoreNLP CoNLL format


def test_parse_spacy_ner_annotator(tiny_corpus, tmp_output):
    _run(
        tiny_corpus,
        tmp_output,
        package="spaCy",
        annotators_var=True,
        annotators_menu_var="NER annotator",
    )
    csvs = [f for f in output_csvs(tmp_output) if "NER" in f]
    assert csvs, "expected an NER_SpaCy csv"
    assert read_rows(csvs[0])


def test_parse_stanza_depparse(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, package="Stanza", parser_var=True)
    csvs = [f for f in output_csvs(tmp_output) if "Stanza" in f]
    assert csvs, "expected a parser (dep)_Stanza csv under depparse_Stanza"
    rows = read_rows(csvs[0])
    assert len(rows) >= 8


# integration ----------------------------------------------------------------


@pytest.mark.integration
def test_parse_corenlp_nn_conll_format(tiny_corpus, tmp_output, corenlp_running):
    # regression check for the 13-column CoreNLP CoNLL table format that
    # tests/fixtures/sample_conll.csv mirrors (consumers index positionally)
    _run(
        tiny_corpus,
        tmp_output,
        package="Stanford CoreNLP",
        parser_var=True,
        parser_menu_var="Neural Network",
    )
    csvs = [f for f in output_csvs(tmp_output) if "CoNLL" in f]
    assert csvs, "expected a CoreNLP_nn_CoNLL csv"
    with open(csvs[0], newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == [
        "ID",
        "Form",
        "Lemma",
        "POS",
        "NER",
        "Head",
        "DepRel",
        "Deps",
        "Clause Tag",
        "Record ID",
        "Sentence ID",
        "Document ID",
        "Document",
    ]
    assert read_rows(csvs[0])
