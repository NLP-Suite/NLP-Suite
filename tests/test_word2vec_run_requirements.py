"""Word2Vec GUI, RUN checks: 'Compute word distances' alone must warn that BERT or Gensim is needed (Roberto,
21 Oct 2026: "If the user selects Compute word distance without selecting either BERT or Gensim, and clicks RUN, it
should display a message saying that BERT or Gensim must be selected")."""

import sys
from unittest.mock import MagicMock, patch

_STUBS = ("gensim", "gensim.models", "numpy", "numpy.linalg")
with patch.dict(sys.modules, {m: MagicMock() for m in _STUBS if m not in sys.modules}):
    import word2vec_distances_util as wd


def test_compute_distances_alone_asks_for_BERT_or_Gensim():
    msg = wd.run_requirements_message(0, 0, 0, 1)
    assert 'BERT' in msg and 'Gensim' in msg and 'Compute word distances' in msg


def test_nothing_selected_still_warns():
    assert 'No option has been selected' in wd.run_requirements_message(0, 0, 0, 0)


def test_any_package_lets_it_run():
    for args in ((1, 0, 0, 1), (0, 1, 0, 1), (1, 1, 0, 0), (0, 0, 1, 0)):
        assert wd.run_requirements_message(*args) == '', args
