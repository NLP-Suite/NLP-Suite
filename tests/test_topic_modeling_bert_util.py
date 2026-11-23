"""BERTopic on a small corpus of whole documents: warn and skip what needs topics, instead of crashing.

On the 60-document HW 5 sample with "split documents" off, BERTopic puts every document in the outlier topic -1,
and hierarchical_topics then stopped with "Found array with 0 sample(s)" (found 21 Nov 2026; tool_sweep recipe
topics_BERTopic_whole). With fewer documents than BERTopic's minimum topic size (10), the fit itself stopped in
HDBSCAN with "k must be less than or equal to the number of training points". Both reproduced with bertopic 0.17
on synthetic embeddings. BERTopic, sentence-transformers and scikit-learn are stubbed: CI installs only pytest.
"""

import importlib
import sys
from unittest.mock import MagicMock, patch

# umap: fix/reproducible-topics-wsi imports UMAP at the top of topic_modeling_bert_util
_STUBS = [
    "bertopic",
    "sentence_transformers",
    "sklearn",
    "sklearn.feature_extraction",
    "sklearn.feature_extraction.text",
    "umap",
]
with patch.dict(sys.modules, {name: MagicMock() for name in _STUBS}):
    sys.modules.pop("topic_modeling_bert_util", None)
    bert_util = importlib.import_module("topic_modeling_bert_util")
    sys.modules.pop("topic_modeling_bert_util", None)


def test_topics_found_leaves_out_the_outliers():
    assert bert_util.topics_found([-1]) == []
    assert bert_util.topics_found([-1, 0, 1]) == [0, 1]
    assert bert_util.topics_found([0, 1, 2]) == [0, 1, 2]


def test_too_few_documents_for_a_topic():
    assert bert_util.too_few_documents(9)
    assert not bert_util.too_few_documents(10)
    assert not bert_util.too_few_documents(60)


def _corpus(tmp_path, n):
    for i in range(n):
        (tmp_path / f"doc{i}.txt").write_text(f"Document {i} about one thing and another.", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    return str(tmp_path), str(out)


def _model(topics):
    model = MagicMock()
    info = MagicMock()
    info.__getitem__.side_effect = lambda column: topics if column == "Topic" else MagicMock()
    model.get_topic_info.return_value = info
    return model


def _run(tmp_path, n_docs, topics):
    inputDir, outputDir = _corpus(tmp_path, n_docs)
    model = _model(topics)
    with (
        patch.object(bert_util, "BERTopic") as BERTopic,
        patch.object(bert_util, "SentenceTransformer"),
        patch.object(bert_util.mb, "showwarning") as warning,
        patch.object(bert_util.os.path, "isdir", return_value=True),  # no model-download alert
    ):
        BERTopic.return_value.fit.return_value = model
        files = bert_util.run_BERTopic(inputDir, outputDir, 0, 0)
    return files, model, warning, outputDir


def test_no_topics_skips_the_hierarchy_and_says_why(tmp_path):
    files, model, warning, outputDir = _run(tmp_path, 60, [-1])
    model.hierarchical_topics.assert_not_called()
    warning.assert_called_once()
    assert "Split documents into sentences" in warning.call_args.kwargs["message"]
    assert files == [f"{outputDir}/topic_info.csv"]  # the documents' topic table is still written


def test_two_topics_get_the_hierarchy(tmp_path):
    files, model, warning, outputDir = _run(tmp_path, 60, [-1, 0, 1])
    model.hierarchical_topics.assert_called_once()
    warning.assert_not_called()
    assert files == [f"{outputDir}/topic_info.csv", f"{outputDir}/topic_hierarchy.html"]


def test_fewer_documents_than_a_topic_needs_stops_before_the_fit(tmp_path):
    inputDir, outputDir = _corpus(tmp_path, 5)
    with (
        patch.object(bert_util, "BERTopic") as BERTopic,
        patch.object(bert_util, "SentenceTransformer") as SentenceTransformer,
        patch.object(bert_util.mb, "showwarning") as warning,
    ):
        assert bert_util.run_BERTopic(inputDir, outputDir, 0, 0) == []
    BERTopic.assert_not_called()
    SentenceTransformer.assert_not_called()
    warning.assert_called_once()
