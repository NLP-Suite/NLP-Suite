"""NRC emotion scores with either NRCLex API (#1719).

NRCLex 4 reads NRCLex(text)'s argument as a lexicon file name and analyzes nothing, so
`.raw_emotion_scores` was missing (NRC crashed) or empty (Character Emotion Arcs scored every
emotion 0 without a warning).
"""

import pytest

import nrclex_util

_LEXICON = {"happy": ["joy", "positive"], "afraid": ["fear", "negative"]}


class NRCLex4:
    """The NRCLex 4 shape: an empty constructor, text through load_raw_text."""

    def __init__(self, lexicon_file="nrc_en.json"):
        self.lexicon_file = lexicon_file

    def load_raw_text(self, text):
        self.raw_emotion_scores = {}
        for word in text.lower().split():
            for emotion in _LEXICON.get(word.strip(".,"), []):
                self.raw_emotion_scores[emotion] = self.raw_emotion_scores.get(emotion, 0) + 1


class NRCLex3:
    """The NRCLex 3 shape: the text goes into the constructor."""

    def __init__(self, text):
        obj = NRCLex4()
        obj.load_raw_text(text)
        self.raw_emotion_scores = obj.raw_emotion_scores


@pytest.mark.parametrize("cls", [NRCLex4, NRCLex3])
def test_both_apis_score_the_text(cls):
    scores = nrclex_util.raw_emotion_scores("I am happy, not afraid.", cls)
    assert scores == {"joy": 1, "positive": 1, "fear": 1, "negative": 1}


def test_text_is_not_passed_as_the_lexicon_file_on_nrclex_4():
    class Spy(NRCLex4):
        def __init__(self, lexicon_file="nrc_en.json"):
            assert lexicon_file == "nrc_en.json", "the text was passed to the constructor"
            super().__init__(lexicon_file)

    assert nrclex_util.raw_emotion_scores("happy", Spy) == {"joy": 1, "positive": 1}


def test_no_emotion_words():
    assert nrclex_util.raw_emotion_scores("the table", NRCLex4) == {}


class TestAllScoresZero:
    EMOTIONS = ["Joy", "Fear"]

    def test_all_zero(self):
        assert nrclex_util.all_scores_zero([{"Joy": 0, "Fear": 0.0}, {"Joy": 0}], self.EMOTIONS)

    def test_one_score(self):
        assert not nrclex_util.all_scores_zero([{"Joy": 0, "Fear": 0}, {"Joy": 0.25}], self.EMOTIONS)
