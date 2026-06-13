import pytest
from conftest import output_csvs, read_rows

try:
    from CoNLL_table_analyzer_main import run_CoNLL_table_analyzer
except (ImportError, SystemExit):
    pytest.skip("CoNLL analyzer dependencies not available", allow_module_level=True)


def _result_csvs(tmp_output):
    # the conll_input dir lives under the same tmp_path as the output dir;
    # exclude the input fixture copy (and its _sentence sibling) from results
    return [f for f in output_csvs(tmp_output) if "conll_input" not in f]


def _run(conll_input_dir, tmp_output, **kwargs):
    args = dict(
        inputFilename="",  # ignored: the analyzer picks the first csv in inputDir
        inputDir=str(conll_input_dir),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="No charts",
        dataTransformation="No transformation",
        searchedCoNLLField="FORM",
        searchField_kw="e.g.: father",
        postag_var="*",
        deprel="*",
        co_postag="*",
        co_deprel="*",
        Begin_K_sent_var=1,
        End_K_sent_var=1,
        all_analyses_var=False,
        all_analyses="*",
        search_token_var=False,
        WordNet_var=False,
        compute_sentence_var=False,
        k_sentences_var=False,
    )
    args.update(kwargs)
    return run_CoNLL_table_analyzer(**args)


def test_no_options_selected_returns_none(conll_input_dir, tmp_output):
    assert _run(conll_input_dir, tmp_output) is None
    assert _result_csvs(tmp_output) == []


def test_search_default_placeholder_keyword_aborts(conll_input_dir, tmp_output):
    assert _run(conll_input_dir, tmp_output, search_token_var=True) is None
    assert _result_csvs(tmp_output) == []


def test_search_token(conll_input_dir, tmp_output):
    _run(conll_input_dir, tmp_output, search_token_var=True, searchField_kw="father")
    csvs = [f for f in _result_csvs(tmp_output) if "CoNLL_search" in f]
    assert len(csvs) == 1
    rows = read_rows(csvs[0])
    assert rows, "expected at least one search result for 'father'"
    assert all(r["Searched Token/Word"] == "father" for r in rows)
    # 'father' appears in both fixture documents
    assert {r["Document ID"] for r in rows} == {"1", "2"}
    # the verb governing 'father' is reported as a related token
    assert {r["Co-occurring Token/Word"] for r in rows} >= {"baked", "loved"}


def test_compute_sentence_writes_next_to_input(conll_input_dir, tmp_output):
    # compute_sentence_table writes <input>_sentence.csv NEXT TO the input
    # file, not in outputDir, and drops the final sentence of the table
    _run(conll_input_dir, tmp_output, compute_sentence_var=True)
    sentence_csv = conll_input_dir / "sample_conll_sentence.csv"
    assert sentence_csv.exists()
    rows = read_rows(str(sentence_csv))
    assert len(rows) >= 1
    assert all(int(r["Sentence length (Number of words/tokens)"]) > 0 for r in rows)


def test_k_sentences(conll_input_dir, tmp_output):
    # uses the stanza pipeline to re-split sentences; hermetic but slow
    _run(conll_input_dir, tmp_output, k_sentences_var=True)
    csvs = [f for f in _result_csvs(tmp_output) if "CoNLL_1-1-sent" in f]
    assert csvs, "expected output under a CoNLL_1-1-sent subdirectory"


def test_k_sentences_short_documents_crash(conll_input_dir, tmp_output):
    # CoNLL_k_sentences_util.k_sent:181 truth-tests a pandas Series whenever a
    # document has <= 2*K sentences, so short documents always crash; see
    # TECH_DEBT.md. The fixture docs have 3 sentences, so K=2 hits the bug.
    with pytest.raises(ValueError, match="truth value of a Series is ambiguous"):
        _run(
            conll_input_dir,
            tmp_output,
            k_sentences_var=True,
            Begin_K_sent_var=2,
            End_K_sent_var=2,
        )


def test_k_sentences_zero_k_returns_none(conll_input_dir, tmp_output):
    assert _run(conll_input_dir, tmp_output, k_sentences_var=True, Begin_K_sent_var=0) is None
    assert _result_csvs(tmp_output) == []


def test_all_analyses_modules_not_ported(conll_input_dir, tmp_output):
    # the seven CoNLL_*_analysis_util modules (noun, clause, adjective, ratio,
    # adverb, verb, function-words) were never ported from the desktop repo;
    # see TECH_DEBT.md. This documents the breakage.
    with pytest.raises(ModuleNotFoundError):
        _run(conll_input_dir, tmp_output, all_analyses_var=True)
