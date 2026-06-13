"""Documenting tests for /word2vec.

None of the word2vec backends were ported from the desktop repo
(word2vec_Gensim_util, WSI_util/WSI_keyterms/WSI_viz, and
BERT_util.word_embeddings_BERT are all missing), so every real option path
crashes; see TECH_DEBT.md. These tests pin down the guard behavior and the
exact failure mode of each backend so a future port has a baseline.
"""

import pytest
from conftest import output_csvs

try:
    from word2vec import run_word2vec
except (ImportError, SystemExit):
    pytest.skip("word2vec dependencies not available", allow_module_level=True)


def _run(tiny_corpus, tmp_output, **kwargs):
    args = dict(
        inputFilename="",
        inputDir=str(tiny_corpus),
        outputDir=str(tmp_output),
        chartPackage="No charts",
        dataTransformation="No transformation",
        remove_stopwords_var=False,
        lemmatize_var=False,
        WSI_var=False,
        BERT_var=False,
        Gensim_var=False,
        sg_menu_var="Skip-Gram",
        vector_size_var=100,
        window_var=5,
        min_count_var=5,
        vis_menu_var="Do not plot",
        dim_menu_var="2D",
        compute_distances_var=False,
        top_words_var=200,
        keywords_var="",
        keywordInput="",
        range4=4,
        range6=6,
        range20=10,
        ngramsDropDown="3-grams (unigrams)",
    )
    args.update(kwargs)
    return run_word2vec(**args)


def test_no_options_selected_returns_none(tiny_corpus, tmp_output):
    assert _run(tiny_corpus, tmp_output) is None
    assert output_csvs(tmp_output) == []


def test_compute_distances_alone_is_a_noop(tiny_corpus, tmp_output):
    # passes the no-option guard but no backend is selected: returns an
    # empty file list and writes nothing
    assert _run(tiny_corpus, tmp_output, compute_distances_var=True) == []
    assert output_csvs(tmp_output) == []


def test_wsi_without_keywords_returns_none(tiny_corpus, tmp_output):
    # the keyword guard fires before the missing WSI_* imports are reached
    # (an empty WSI_* subdirectory is still created)
    assert _run(tiny_corpus, tmp_output, WSI_var=True, keywordInput="") is None
    assert output_csvs(tmp_output) == []


def test_wsi_backend_missing(tiny_corpus, tmp_output):
    with pytest.raises(ModuleNotFoundError):
        _run(tiny_corpus, tmp_output, WSI_var=True, keywordInput="bread,rocket")


def test_gensim_backend_missing(tiny_corpus, tmp_output):
    with pytest.raises(ModuleNotFoundError):
        _run(tiny_corpus, tmp_output, Gensim_var=True)


def test_bert_backend_missing(tiny_corpus, tmp_output):
    # BERT_util exists (sentiment-only port) but word_embeddings_BERT was
    # never ported; fails before any model download
    with pytest.raises(AttributeError):
        _run(tiny_corpus, tmp_output, BERT_var=True)
