import pathlib

import pytest

try:
    from topic_modeling import run_topic_modeling
except (ImportError, SystemExit):
    pytest.skip("topic_modeling dependencies not available", allow_module_level=True)


def _run(tiny_corpus, tmp_output, **kwargs):
    args = dict(
        inputDir=str(tiny_corpus),
        outputDir=str(tmp_output),
        chartPackage="No charts",
        dataTransformation="No transformation",
        num_topics=2,
        BERT_var=False,
        split_docs_var=False,
        MALLET_var=False,
        optimize_intervals_var=False,
        Gensim_var=False,
        remove_stopwords_var=True,
        lemmatize_var=False,
        nounsOnly_var=False,
        Gensim_MALLET_var=False,
    )
    args.update(kwargs)
    return run_topic_modeling(**args)


def test_no_options_selected_returns_none(tiny_corpus, tmp_output):
    assert _run(tiny_corpus, tmp_output) is None
    assert list(pathlib.Path(tmp_output).iterdir()) == []


def test_gensim(tiny_corpus, tmp_output):
    files = _run(tiny_corpus, tmp_output, Gensim_var=True)
    # outputs land in a TM-Gensim subdirectory of the output dir
    subdirs = [p for p in pathlib.Path(tmp_output).iterdir() if p.is_dir()]
    assert any("TM-Gensim" in p.name for p in subdirs)
    produced = list(pathlib.Path(tmp_output).rglob("*.csv")) + list(pathlib.Path(tmp_output).rglob("*.html"))
    assert produced, "expected Gensim to write csv/html outputs"
    if files:  # returned list should only reference files that exist
        assert all(pathlib.Path(f).exists() for f in files if isinstance(f, str) and f)


def test_gensim_single_file_dir_raises(tmp_path, tmp_output, fixture_txt):
    # topic modeling requires more than one document
    single = tmp_path / "single"
    single.mkdir()
    (single / "only.txt").write_text(fixture_txt.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError):
        _run(single, tmp_output, Gensim_var=True)
