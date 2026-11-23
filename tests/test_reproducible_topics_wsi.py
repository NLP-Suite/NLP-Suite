"""BERTopic, MALLET and WSI give the same result for the same corpus on every RUN.

Running tests/tool_sweep.py twice on the same zip (22 Nov 2026) gave different topics, keywords and sense clusters
each time, so a student could not reproduce a homework answer. BERTopic's UMAP and MALLET's sampler were seeded at
random. WSI's k-means was seeded, but its vectors were shuffled at random first, so k-means started from different
points; and several outputs were written in set order, which changes with Python's per-process hash seed.
The heavy libraries are stubbed: CI installs only pytest.
"""

import importlib
import sys
from unittest.mock import MagicMock, patch

for _mod in ("sklearn", "sklearn.metrics", "sklearn.cluster", "sklearn.metrics.pairwise", "torch", "torch.nn"):
    sys.modules.setdefault(_mod, MagicMock())
for _mod in ("transformers", "tqdm"):
    sys.modules.setdefault(_mod, MagicMock())

import WSI_classes  # noqa: E402

with patch.dict(sys.modules, {m: MagicMock() for m in ("file_converter_util",) if m not in sys.modules}):
    import topic_modeling_mallet_util as mallet  # noqa: E402


def test_WSI_shuffle_is_the_same_every_run():
    data = list(range(50))
    first = WSI_classes.seeded_shuffle(list(data))
    assert first == WSI_classes.seeded_shuffle(list(data))
    assert sorted(first) == data and first != data  # still shuffled, as k-means expects


def test_MALLET_train_topics_gets_a_fixed_seed():
    _, train_cmd = mallet.mallet_commands("bin/mallet", "in", "f.mallet", 20, True, "s.gz", "k.tsv", "c")
    i = train_cmd.index("--random-seed")
    assert train_cmd[i + 1] == str(mallet.RANDOM_SEED) and mallet.RANDOM_SEED != 0  # 0 means "use the clock"


def test_BERTopic_UMAP_gets_a_fixed_seed(tmp_path):
    stubs = {m: MagicMock() for m in ("bertopic", "sentence_transformers", "umap")}
    stubs.update({m: MagicMock() for m in ("sklearn", "sklearn.feature_extraction", "sklearn.feature_extraction.text")})
    with patch.dict(sys.modules, stubs):
        sys.modules.pop("topic_modeling_bert_util", None)
        bert_util = importlib.import_module("topic_modeling_bert_util")
        sys.modules.pop("topic_modeling_bert_util", None)
    for i in range(12):
        (tmp_path / f"d{i}.txt").write_text("text", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    with (
        patch.object(bert_util, "UMAP") as UMAP,
        patch.object(bert_util, "BERTopic") as BERTopic,
        patch.object(bert_util, "SentenceTransformer"),
        patch.object(bert_util.os.path, "isdir", return_value=True),
    ):
        try:
            bert_util.run_BERTopic(str(tmp_path), str(out), 0, 0)
        except Exception:  # the stubbed model's outputs are mocks; only the construction matters here
            pass
    assert UMAP.call_args.kwargs["random_state"] == bert_util.RANDOM_SEED
    assert BERTopic.call_args.kwargs["umap_model"] is UMAP.return_value
