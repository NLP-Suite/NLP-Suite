"""spaCy CoNLL table: ID and HEAD must be sentence-level and 1-based, as in the CoreNLP and Stanza tables.

spaCy's ``token.head.i`` is a document-level index and the root points at itself; ``conll_head`` converts it.
The tokens below are plain objects with the three attributes the helper reads (``i``, ``head``, and the
sentence's ``start``), so no spaCy model is needed.
"""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

with patch.dict(sys.modules, {"constants_util": MagicMock(), "parsers_annotators_visualization_util": MagicMock()}):
    try:
        from spaCy_util import conll_head
    except (ImportError, SystemExit):  # pragma: no cover - defensive
        pytest.skip("spaCy_util dependencies not available", allow_module_level=True)


def _sentence(start, heads):
    """Tokens of one sentence starting at document index ``start``; ``heads`` are document indices."""
    tokens = [SimpleNamespace(i=start + k) for k in range(len(heads))]
    by_index = {t.i: t for t in tokens}
    for k, t in enumerate(tokens):
        t.head = by_index[heads[k]]
    return SimpleNamespace(start=start), tokens


def test_root_head_is_zero():
    # "Tom ate apples": 'ate' (index 1) is the root and spaCy points it at itself
    sent, (tom, ate, apples) = _sentence(0, [1, 1, 1])
    assert conll_head(ate, sent) == 0
    assert conll_head(tom, sent) == 2
    assert conll_head(apples, sent) == 2


def test_heads_in_a_later_sentence_are_sentence_level():
    # second sentence of a document, starting at token 7: 'She left early', root 'left' at index 8
    sent, (she, left, early) = _sentence(7, [8, 8, 8])
    assert conll_head(she, sent) == 2  # not 8, the document-level index
    assert conll_head(left, sent) == 0
    assert conll_head(early, sent) == 2
