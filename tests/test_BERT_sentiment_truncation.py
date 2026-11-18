"""BERT sentiment: sentences over 512 tokens are truncated, not passed whole (#1722).

The cardiffnlp roBERTa tokenizers set no length limit of their own, so truncation=True without
max_length let a 586-token sentence reach a model with 514 positions, and Shape of Stories (whose
default method is BERT) and the sentiment GUI's BERT option stopped with a tensor-size RuntimeError.
"""

import sys
from unittest.mock import MagicMock, patch

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


def test_the_pipeline_is_capped_at_512_tokens():
    assert BERT_util.SENTIMENT_PIPELINE_KWARGS == {"truncation": True, "max_length": 512}


def test_sentiment_analysis_BERT_builds_the_pipeline_with_the_cap(tmp_path):
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    with patch.object(BERT_util, "pipeline") as pipeline, patch.object(BERT_util, "mb"):
        BERT_util.sentiment_analysis_BERT(str(empty), str(tmp_path), "out.csv", "", 1, "empty.txt", "some/model")
    _, kwargs = pipeline.call_args
    assert kwargs["truncation"] is True
    assert kwargs["max_length"] == 512
