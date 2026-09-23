"""BERT word embeddings (BERT_util.word_embeddings_BERT): which words, from which sentences.

The vector csv used to loop over the leftover `sentences` variable, so every document was written
with the LAST document's sentences. The Lemmatize option was a no-op, because an import inside the
loop replaced the lemmatizing pipeline with Stanza_functions_util's tokenize-only one.
"""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# stubbed only while BERT_util is imported: a lasting stub of statistics_txt_util (say) would
# replace the real module for every test collected after this one
_STUBS = (
    "transformers",
    "sentence_transformers",
    "torch",
    "contextualSpellCheck",
    "summarizer",
    "plotly",
    "plotly.express",
    "sklearn",
    "sklearn.feature_extraction",
    "sklearn.feature_extraction.text",
    "sklearn.metrics",
    "sklearn.metrics.pairwise",
    "sklearn.manifold",
    "word2vec_tsne_plot_util",
    "word2vec_distances_util",
    "IO_internet_util",
    "statistics_txt_util",
)
with patch.dict(sys.modules, {m: MagicMock() for m in _STUBS if m not in sys.modules}):
    import BERT_util


def _doc(*sentences):
    """A Stanza-like doc: each sentence a list of (text, lemma) pairs."""
    return SimpleNamespace(
        sentences=[SimpleNamespace(words=[SimpleNamespace(text=t, lemma=lem) for t, lem in s]) for s in sentences]
    )


class TestStanzaWords:
    def test_every_sentence_not_just_the_last(self):
        doc = _doc([("It", "it"), ("rained", "rain")], [("We", "we"), ("left", "leave")])
        assert BERT_util.stanza_words(doc, lemmatize=False) == ["It", "rained", "We", "left"]

    def test_lemmas_when_lemmatizing(self):
        doc = _doc([("It", "it"), ("rained", "rain")], [("We", "we"), ("left", "leave")])
        assert BERT_util.stanza_words(doc, lemmatize=True) == ["it", "rain", "we", "leave"]

    def test_missing_lemma_falls_back_to_text(self):
        assert BERT_util.stanza_words(_doc([("Zyx", None)]), lemmatize=True) == ["Zyx"]


class TestCsvWordRows:
    def test_each_document_keeps_its_own_sentences(self):
        doc_sentences = [
            ("a.txt", [("Cats purr.", ["cats", "purr"])]),
            ("b.txt", [("Dogs bark.", ["dogs", "bark"]), ("Birds sing.", ["birds", "sing"])]),
        ]
        rows = list(BERT_util.csv_word_rows(doc_sentences, {"cats", "purr", "dogs", "bark", "birds", "sing"}))
        assert rows == [
            (1, "a.txt", 1, "Cats purr.", "cats"),
            (1, "a.txt", 1, "Cats purr.", "purr"),
            (2, "b.txt", 1, "Dogs bark.", "dogs"),
            (2, "b.txt", 1, "Dogs bark.", "bark"),
            (2, "b.txt", 2, "Birds sing.", "birds"),
            (2, "b.txt", 2, "Birds sing.", "sing"),
        ]

    def test_drops_words_that_were_not_embedded(self):
        doc_sentences = [("a.txt", [("The cat purrs.", ["The", "cat", "purrs", "."])])]
        rows = list(BERT_util.csv_word_rows(doc_sentences, {"cat", "purrs"}))
        assert [r[-1] for r in rows] == ["cat", "purrs"]
