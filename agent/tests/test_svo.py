import pytest
from conftest import output_csvs, read_rows

try:
    import spaCy_util
    from SVO import run_svo
except (ImportError, SystemExit):
    pytest.skip("SVO dependencies not available", allow_module_level=True)


@pytest.fixture(autouse=True)
def _no_spacy_download(monkeypatch):
    # spaCy_annotate shells out to `spacy download` on every call and bails
    # out on failure; the model is preinstalled in the agent image, so make
    # the download a no-op to keep tests offline-safe
    monkeypatch.setattr(spaCy_util.subprocess, "check_call", lambda *a, **k: 0)


def _run(tiny_corpus, tmp_output, **kwargs):
    args = dict(
        inputFilename="",
        inputDir=str(tiny_corpus),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="No charts",
        dataTransformation="No transformation",
        coref_var=False,
        manual_coref_var=False,
        normalized_NER_date_extractor_var=False,
        package_var="",
        gender_var=False,
        quote_var=False,
        subjects_dict_path_var="",
        verbs_dict_path_var="",
        objects_dict_path_var="",
        filter_subjects=False,
        filter_verbs=False,
        filter_objects=False,
        lemmatize_subjects=False,
        lemmatize_verbs=False,
        lemmatize_objects=False,
        gephi_var=False,
        google_earth_var=False,
    )
    args.update(kwargs)
    return run_svo(**args)


def test_csv_input_without_svo_in_name_returns_none(tiny_corpus, tmp_output, fixture_csv):
    assert _run(tiny_corpus, tmp_output, inputFilename=str(fixture_csv)) is None
    assert output_csvs(tmp_output) == []


def test_filter_without_lemmatize_returns_none(tiny_corpus, tmp_output):
    assert (
        _run(
            tiny_corpus,
            tmp_output,
            package_var="spaCy",
            filter_subjects=True,
            lemmatize_subjects=False,
        )
        is None
    )
    assert output_csvs(tmp_output) == []


def test_svo_spacy(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, package_var="spaCy")
    svo_csvs = [f for f in output_csvs(tmp_output) if "SVO_spaCy" in f.rsplit("/", 1)[-1]]
    assert len(svo_csvs) == 1
    rows = read_rows(svo_csvs[0])
    # the cooking docs have clear S-V-O sentences ("The chef baked fresh bread...")
    assert len(rows) >= 1
    assert "Subject (S)" in rows[0]
    assert "Verb (V)" in rows[0]
    assert "Object (O)" in rows[0]
    # note: with the SVO annotator spaCy_util writes only the SVO table
    # (the CoNLL table is written for the NER/parse/sentiment annotators)


def test_svo_stanza(tiny_corpus, tmp_output):
    _run(tiny_corpus, tmp_output, package_var="Stanza")
    svo_csvs = [f for f in output_csvs(tmp_output) if "SVO_Stanza" in f.rsplit("/", 1)[-1]]
    assert len(svo_csvs) == 1
    rows = read_rows(svo_csvs[0])
    assert len(rows) >= 1
    assert "Subject (S)" in rows[0]
    assert [f for f in output_csvs(tmp_output) if "CoNLL_Stanza" in f]


@pytest.mark.integration
def test_svo_corenlp(tiny_corpus, tmp_output, corenlp_running):
    _run(tiny_corpus, tmp_output, package_var="Stanford CoreNLP")
    svo_csvs = [f for f in output_csvs(tmp_output) if "SVO" in f.rsplit("/", 1)[-1]]
    assert svo_csvs, "expected an SVO csv from the CoreNLP annotator"
    rows = read_rows(svo_csvs[0])
    assert len(rows) >= 1
    assert "Subject (S)" in rows[0]
    assert "Verb (V)" in rows[0]
    assert "Object (O)" in rows[0]
