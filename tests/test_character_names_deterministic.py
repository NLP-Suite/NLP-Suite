"""Character Emotion Arcs names each character the same way on every RUN.

A sentence's PERSON mentions come from a set, whose order changes with each process's hash seed. The first
variant registered becomes the character's name for the whole corpus, so a sentence with both "Robin" and
"Robin Ellacott" named her "Robin" one run and "Robin Ellacott" the next, and the per-character charts were
named after either (found 22 Nov 2026 by running tests/tool_sweep.py twice). The mentions of a sentence are now
taken fullest name first, then alphabetically, and its rows written in alphabetical order.
"""

from itertools import permutations
import sys
from unittest.mock import MagicMock, patch

_STUBS = ["matplotlib", "matplotlib.patches", "matplotlib.pyplot", "nrclex_util"]
with patch.dict(sys.modules, {m: MagicMock() for m in _STUBS}):
    import character_emotion_arcs_util as arcs


def test_the_order_of_the_mentions_does_not_matter():
    mentions = ["Robin", "Robin Ellacott", "Strike"]
    results = {tuple(arcs.characters_of_sentence(list(order), {})) for order in permutations(mentions)}
    assert results == {("Robin Ellacott", "Strike")}


def test_the_fuller_name_names_the_character_for_the_rest_of_the_corpus():
    for order in (["Robin", "Robin Ellacott"], ["Robin Ellacott", "Robin"]):
        canonical_map = {}
        assert arcs.characters_of_sentence(order, canonical_map) == ["Robin Ellacott"]
        assert arcs.characters_of_sentence({"Robin"}, canonical_map) == ["Robin Ellacott"]


def test_no_mention_is_the_narrator():
    assert arcs.characters_of_sentence(set(), {}) == ["_NARRATOR/UNATTRIBUTED_"]
