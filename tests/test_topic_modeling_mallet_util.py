"""MALLET topic modeling: the command lines, and when a run counts as failed.

--optimize-interval used to receive the NUMBER OF TOPICS (so 5 topics re-optimized every 5 iterations and
50 topics every 50); it is an iteration count, fixed here at 20. The failure check fired only when BOTH
output files were missing, so a half-finished run went on to the csv conversion.
"""

import os
import sys
from unittest.mock import MagicMock, patch

with patch.dict(sys.modules, {m: MagicMock() for m in ("file_converter_util",) if m not in sys.modules}):
    import topic_modeling_mallet_util as mallet


def _commands(optimize, num_topics=50):
    return mallet.mallet_commands("bin/mallet", "in dir", "f.mallet", num_topics, optimize, "s.gz", "k.tsv", "c")


def test_import_command():
    import_cmd, _ = _commands(optimize=True)
    assert import_cmd == [
        "bin/mallet",
        "import-dir",
        "--input",
        "in dir",
        "--output",
        "f.mallet",
        "--keep-sequence",
        "--remove-stopwords",
    ]


def test_optimize_interval_is_not_the_number_of_topics():
    _, train_cmd = _commands(optimize=True, num_topics=50)
    i = train_cmd.index("--optimize-interval")
    assert train_cmd[i + 1] == str(mallet.OPTIMIZE_INTERVAL) == "20"
    assert train_cmd[train_cmd.index("--num-topics") + 1] == "50"


def test_no_optimize_flag_when_off():
    _, train_cmd = _commands(optimize=False)
    assert "--optimize-interval" not in train_cmd


def test_train_command_outputs():
    _, train_cmd = _commands(optimize=False)
    assert train_cmd[-6:] == ["--output-state", "s.gz", "--output-topic-keys", "k.tsv", "--output-doc-topics", "c"]


def test_either_missing_output_is_a_failure(tmp_path):
    keys, comp = tmp_path / "keys.tsv", tmp_path / "comp"
    keys.write_text("0\t1.0\tword\n")
    assert mallet.mallet_outputs_missing(str(keys), str(comp)) == [str(comp)]
    comp.write_text("0\tdoc\t1.0\n")
    assert mallet.mallet_outputs_missing(str(keys), str(comp)) == []
    os.remove(keys)
    assert mallet.mallet_outputs_missing(str(keys), str(comp)) == [str(keys)]


def test_shares_gensim_corpus_size_advice():
    # an error only for 0 or 1 documents; advice, not a default-No dialog, under 50
    assert mallet.corpus_size_advice(1)[0] == "error"
    assert mallet.corpus_size_advice(20)[0] == "advice"
    assert mallet.corpus_size_advice(872)[0] == ""
