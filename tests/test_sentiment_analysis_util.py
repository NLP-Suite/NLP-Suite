"""sentiment_analysis_main's routing and output bookkeeping (#1719, #1720).

- "Character Emotion Arcs (NER + NRC)" contains "NRC", and the NRC test came first, so choosing
  the arcs ran NRC instead.
- An annotator that produced nothing returned [], and outputFiles[0] stopped the '*' run there,
  so every algorithm after spaCy was skipped without a word.
"""

import sentiment_analysis_util as u


class TestSelectedAlgorithms:
    def test_character_arcs_is_not_routed_to_nrc(self):
        assert u.selected_algorithms("   Character Emotion Arcs (NER + NRC)") == {"Character Emotion Arcs"}

    def test_nrc(self):
        assert u.selected_algorithms("   NRC (emotion wheel)") == {"NRC"}

    def test_each_menu_label(self):
        cases = {
            "   BERT (English model)": "BERT",
            "   BERT (Multilingual model)": "BERT",
            "   Stanford CoreNLP": "CoreNLP",
            "   Stanza": "Stanza",
            "   ANEW": "ANEW",
            "   hedonometer": "hedonometer",
            "   spaCy (TextBlob)": "spaCy",
            "   SentiWordNet": "SentiWordNet",
            "   VADER": "VADER",
        }
        for label, algorithm in cases.items():
            assert u.selected_algorithms(label) == {algorithm}, label

    def test_star_runs_everything_but_the_arcs(self):
        chosen = u.selected_algorithms("*")
        assert chosen == set(u.ALL_ALGORITHMS)
        assert "Character Emotion Arcs" not in chosen

    def test_headings_select_nothing(self):
        for heading in ("", "Large Language Models (LLM):", "Dictionary approaches:", "Character-level:"):
            assert u.selected_algorithms(heading) == set()


class TestAddOutputs:
    def test_empty_list_is_no_output_and_does_not_raise(self):
        files = []
        assert u.add_outputs([], files) == ""
        assert files == []

    def test_none(self):
        files = []
        assert u.add_outputs(None, files) == ""

    def test_a_single_path(self):
        files = ["a.csv"]
        assert u.add_outputs("b.csv", files) == "b.csv"
        assert files == ["a.csv", "b.csv"]

    def test_a_list_returns_its_first_file(self):
        files = []
        assert u.add_outputs(["scores.csv", "chart.xlsx"], files) == "scores.csv"
        assert files == ["scores.csv", "chart.xlsx"]


class TestFailedMessage:
    def test_none_failed(self):
        assert u.failed_algorithms_message([]) == ""

    def test_lists_each_one(self):
        msg = u.failed_algorithms_message(["spaCy", "NRC"])
        assert "spaCy" in msg and "NRC" in msg


class TestShapeOfStoriesScoresReady:
    """Step 2 of Shape of Stories needs a scores csv; the txt folder used to reach the vectorizer (#1722)."""

    def test_step_1_wrote_scores(self):
        assert u.sentiment_scores_ready(1, "/out/NLP_BERT_sentiment.csv", "", "/corpus")

    def test_step_1_produced_nothing(self):
        assert not u.sentiment_scores_ready(1, "/corpus", "", "/corpus")

    def test_csv_input_without_step_1(self, tmp_path):
        assert u.sentiment_scores_ready(0, str(tmp_path / "scores.csv"), str(tmp_path / "scores.csv"), "")

    def test_txt_folder_without_step_1(self, tmp_path):
        (tmp_path / "a.txt").write_text("x", encoding="utf-8")
        assert not u.sentiment_scores_ready(0, str(tmp_path), "", str(tmp_path))

    def test_folder_of_csv_without_step_1(self, tmp_path):
        (tmp_path / "a.csv").write_text("x", encoding="utf-8")
        assert u.sentiment_scores_ready(0, str(tmp_path), "", str(tmp_path))
