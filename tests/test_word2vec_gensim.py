"""Gensim Word2Vec distances: look words up in the form the model was trained on.

With Lemmatize on (the GUI default) the vocabulary is lemmas, but the distance code looked up the
surface 'Word' column, so every inflected form raised KeyError and its pairs were silently dropped
(171 of 435 top-30 pairs kept on a 40-document sample). "Remove stopwords & punctuation" also let
"...", "'s" and "--" through as top words.
"""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

_STUBS = ("gensim", "gensim.models", "numpy", "numpy.linalg")
with patch.dict(sys.modules, {m: MagicMock() for m in _STUBS if m not in sys.modules}):
    import word2vec_distances_util
    import word2vec_Gensim_util


class TestIsNoiseToken:
    def test_multi_character_punctuation(self):
        for tok in ("...", "--", "''", "—", "?!"):
            assert word2vec_Gensim_util.is_noise_token(tok), tok

    def test_clitics(self):
        for tok in ("'s", "’s", "n't", "N'T", "'ll"):
            assert word2vec_Gensim_util.is_noise_token(tok), tok

    def test_single_characters(self):
        assert word2vec_Gensim_util.is_noise_token("a")
        assert word2vec_Gensim_util.is_noise_token(",")

    def test_real_words_kept(self):
        for tok in ("woman", "don", "U.S.", "e-mail", "1990s", "et"):
            assert not word2vec_Gensim_util.is_noise_token(tok), tok


class TestVocabularyColumn:
    def test_lemma_when_lemmatized(self):
        df = SimpleNamespace(columns=["Word", "Lemma", "Vector"])
        assert word2vec_distances_util.vocabulary_column(df) == "Lemma"

    def test_word_otherwise(self):
        df = SimpleNamespace(columns=["Word", "Vector"])
        assert word2vec_distances_util.vocabulary_column(df) == "Word"


class TestSplitKeywords:
    def test_present_and_missing_in_input_order(self):
        vocab = {"say": 0, "know": 1, "time": 2}
        got = word2vec_distances_util.split_keywords(" say, said ,know,,time,years, say", vocab)
        assert got == (["say", "know", "time"], ["said", "years"])

    def test_case_is_kept(self):
        assert word2vec_distances_util.split_keywords("May", {"may"}) == ([], ["May"])
