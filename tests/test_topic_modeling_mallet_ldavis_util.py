"""MALLET's topic model in the pyLDAvis view (topic_modeling_mallet_ldavis_util): the state file MALLET writes with
--output-state is read into the five arrays pyLDAvis.prepare takes."""

import gzip

import topic_modeling_mallet_ldavis_util as ml

STATE = (
    "#doc source pos typeindex type topic\n#alpha : 0.5 0.5\n#beta : 0.01\n"
    "0 C:/x/a.txt 0 0 army 1\n0 C:/x/a.txt 1 1 rain 0\n2 C:/x/c.txt 0 1 rain 0\n"
)


def test_the_state_file_is_read(tmp_path):
    p = tmp_path / "state.gz"
    with gzip.open(str(p), "wt", encoding="utf-8") as fh:
        fh.write(STATE)
    alpha, beta, rows = ml.read_state(str(p))
    assert alpha == [0.5, 0.5] and beta == 0.01
    assert rows == [(0, "army", 1), (0, "rain", 0), (2, "rain", 0)]


def test_the_arrays_pyldavis_takes():
    alpha, beta = [0.5, 0.5], 0.01
    rows = [(0, "army", 1), (0, "rain", 0), (2, "rain", 0)]
    tt, dt, lengths, vocab, tf = ml.ldavis_inputs(alpha, beta, rows)
    assert vocab == ["army", "rain"] and tf == [1, 2] and lengths == [2, 0, 1]
    assert all(abs(sum(r) - 1) < 1e-9 for r in tt) and all(abs(sum(r) - 1) < 1e-9 for r in dt)
    assert tt[1][0] > tt[1][1]  # topic 1 is the army topic


def test_an_empty_state_draws_nothing(tmp_path):
    p = tmp_path / "state.gz"
    with gzip.open(str(p), "wt", encoding="utf-8") as fh:
        fh.write("#doc source pos typeindex type topic\n#alpha : 0.5\n#beta : 0.01\n")
    assert ml.mallet_to_ldavis(str(p), str(tmp_path / "x.html")) == ""


def test_a_documents_number_is_read_off_its_file_name():
    assert ml.document_number("C:/x/doc00042.txt") == 42 and ml.document_number("C:/x/notes.txt") is None


def test_the_mallet_tool_writes_the_view():
    # the Suite's MALLET tool calls this module after training (checked as text: it imports the GUI modules)
    import os

    src = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "topic_modeling_mallet_util.py"
    )
    with open(src, encoding="utf-8-sig") as f:
        s = f.read()
    assert "topic_modeling_mallet_ldavis_util.mallet_to_ldavis(" in s and "NLP-MALLET_topics_pyLDAvis.html" in s


def test_a_source_path_with_spaces_is_read(tmp_path):
    # MALLET writes each document's file path into the state line, and a path can hold spaces
    p = tmp_path / "state.gz"
    with gzip.open(str(p), "wt", encoding="utf-8") as fh:
        fh.write(
            "#doc source pos typeindex type topic\n#alpha : 0.5 0.5\n#beta : 0.01\n"
            "0 C:/my docs/Thread_Anne Smith letter.txt 0 0 army 1\n"
            "1 C:/my docs/second file.txt 0 1 rain 0\n"
        )
    _alpha, _beta, rows = ml.read_state(str(p))
    assert rows == [(0, "army", 1), (1, "rain", 0)]
