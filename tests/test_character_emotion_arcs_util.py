"""Tests for src/character_emotion_arcs_util.py, one file per module (folded from 2 files, 23 Nov 2026).

From test_character_names_deterministic.py:

Character Emotion Arcs names each character the same way on every RUN.

A sentence's PERSON mentions come from a set, whose order changes with each process's hash seed. The first
variant registered becomes the character's name for the whole corpus, so a sentence with both "Robin" and
"Robin Ellacott" named her "Robin" one run and "Robin Ellacott" the next, and the per-character charts were
named after either (found 22 Nov 2026 by running tests/tool_sweep.py twice). The mentions of a sentence are now
taken fullest name first, then alphabetically, and its rows written in alphabetical order.

From test_emotion_arc_html.py:

The emotion arcs as an interactive file, and the binning that makes them readable.

The PNG plots eight emotions over every appearance a character has - about 5,000 for Hermione,
40,000 points in one chart. The lines cross so often that no arc can be followed. Grouping the
appearances into ~120 equal-count bins and drawing each bin's MEAN keeps the shape and makes the
line followable.

The property that matters: binning must not move the level. A count-weighted mean of the bins has
to equal the character's overall mean, or the chart is quietly reporting different numbers from
the summary csv sitting next to it.
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


# ---- formerly tests/test_emotion_arc_html.py ----------------------------------------------------------------

import importlib.util  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
from unittest.mock import MagicMock  # noqa: E402

import _real_pandas  # noqa: E402
import pytest  # noqa: E402

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


@pytest.fixture(scope="module")
def arcs_emotion_arc_html():
    """Load the module against the REAL pandas, then put conftest's stub back.

    conftest stubs pandas for every test, which is right for the GUI-coupled modules but would make
    this file a no-op: binning is arithmetic over a DataFrame, and a MagicMock frame proves nothing.
    The stub is restored afterwards so the other test modules are unaffected; the module under test
    keeps its own reference to the real pandas, so the tests still work on real frames.
    """
    # numpy has to come out with it: real pandas imports numpy, and importing it against a
    # MagicMock numpy fails in a way that is easy to read as "no pandas here".
    # PIL comes out too: matplotlib is NOT stubbed, and the real matplotlib imports
    # PIL.PngImagePlugin, which a MagicMock 'PIL' cannot provide.
    # pandas and numpy go through _real_pandas, which imports them once per run: a second fresh numpy
    # import (by another test file) breaks the first copy.
    roots = ("PIL",)
    saved = {k: v for k, v in sys.modules.items() if k in roots or k.startswith(tuple(r + "." for r in roots))}
    # matplotlib is STUBBED for the load, not imported. Neither function under test draws anything,
    # and the real matplotlib brings its own trouble here: already imported against the MagicMock
    # numpy it reports a metaclass conflict, and imported fresh it needs native DLLs that are not on
    # PATH in every environment. Neither failure has anything to do with the binning being tested.
    purge = ("matplotlib", "mpl_toolkits")

    def _drop(names):
        for k in [k for k in list(sys.modules) if k in names or k.startswith(tuple(n + "." for n in names))]:
            del sys.modules[k]

    for k in saved:
        del sys.modules[k]
    _drop(purge)
    # nrclex for the same reason: the real one pulls in textblob, which subclasses nltk - and
    # against conftest's MagicMock nltk that is a metaclass conflict. Scoring a sentence is not
    # what these tests are about; binning already-scored rows is.
    for name in ("matplotlib", "matplotlib.pyplot", "matplotlib.patches", "nrclex"):
        sys.modules[name] = MagicMock()
    try:
        _pandas, saved_pd = _real_pandas.swap_in()
    except ImportError as exc:
        _drop(roots)
        _drop(purge)
        sys.modules.update(saved)
        pytest.skip("real pandas not available: %s" % exc)
    try:
        spec = importlib.util.spec_from_file_location(
            "_arcs_html", os.path.join(_SRC, "character_emotion_arcs_util.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:
        _real_pandas.swap_out(saved_pd)
        _drop(roots)
        _drop(purge)
        sys.modules.update(saved)
        pytest.skip("could not load the module against real pandas: %s" % exc)

    # The real pandas has to STAY in sys.modules while these tests run: it imports its own
    # submodules lazily (pandas.core.indexes.range on the first DataFrame), and restoring the stub
    # now would break those imports mid-test. The stub goes back when this file is done, so the
    # rest of the suite sees exactly what conftest set up.
    yield mod
    _real_pandas.swap_out(saved_pd)
    _drop(roots)
    _drop(purge)
    sys.modules.update(saved)


@pytest.fixture(scope="module")
def pd(arcs_emotion_arc_html):
    """The real pandas the module under test is holding."""
    return arcs_emotion_arc_html.pd


def _frame(arcs_emotion_arc_html, n=500, characters=("Hermione",)):
    """A frame shaped like the real one: eight emotion columns, one row per appearance."""
    rows = []
    for c_i, character in enumerate(characters):
        for i in range(n):
            row = {"Character": character, "Sentence ID": i, "Corpus Position": i + c_i}
            for e_i, e in enumerate(arcs_emotion_arc_html.EIGHT_EMOTIONS):
                # something with a shape, and different per emotion and per character
                row[e.capitalize()] = ((i * (e_i + 1) + c_i * 7) % 23) / 100.0
            rows.append(row)
    return arcs_emotion_arc_html.pd.DataFrame(rows)


class TestArcByBin:
    def test_the_binned_mean_equals_the_overall_mean(self, arcs_emotion_arc_html):
        """Equal-count bins, so weighting each bin by its count must recover the true mean. If this
        drifts, the chart and the summary csv disagree about the same character."""
        df = _frame(arcs_emotion_arc_html, n=503)
        labels, means, counts = arcs_emotion_arc_html.arc_by_bin(df, 120)
        assert sum(counts) == len(df)
        for e in arcs_emotion_arc_html.EIGHT_EMOTIONS:
            col = e.capitalize()
            weighted = sum(v * n for v, n in zip(means[col], counts)) / sum(counts)
            assert weighted == pytest.approx(float(df[col].mean()), abs=1e-9)

    def test_every_appearance_lands_in_exactly_one_bin(self, arcs_emotion_arc_html):
        df = _frame(arcs_emotion_arc_html, n=137)
        _, _, counts = arcs_emotion_arc_html.arc_by_bin(df, 40)
        assert sum(counts) == 137
        assert all(c >= 1 for c in counts)

    def test_asking_for_more_bins_than_rows_does_not_invent_empty_ones(self, arcs_emotion_arc_html):
        """An empty bin in a line chart reads as calm, not as absence."""
        df = _frame(arcs_emotion_arc_html, n=7)
        labels, means, counts = arcs_emotion_arc_html.arc_by_bin(df, 120)
        assert len(counts) == 7
        assert all(c >= 1 for c in counts)

    def test_an_empty_frame_is_skipped_not_an_exception(self, arcs_emotion_arc_html, pd):
        """A character with no rows is a reason to draw no chart, not to end a profile."""
        labels, means, counts = arcs_emotion_arc_html.arc_by_bin(pd.DataFrame(columns=["Anger"]), 20)
        assert (labels, means, counts) == ([], {}, [])

    def test_it_follows_narrative_order_not_the_frame_order(self, arcs_emotion_arc_html):
        """The caller sorts; this must not reorder underneath it. First bin holds the first rows."""
        df = _frame(arcs_emotion_arc_html, n=100)
        _, means, _ = arcs_emotion_arc_html.arc_by_bin(df, 10)
        first_ten = df.iloc[0:10]["Anger"].mean()
        assert means["Anger"][0] == pytest.approx(first_ten)


class TestEmotionArcHtml:
    def _data(self, path):
        h = open(path, encoding="utf-8").read()
        return json.loads(h[h.index("var DATA =") + 10 : h.index("\nvar PAD")].strip().rstrip(";")), h

    def test_it_writes_one_file_covering_every_character(self, arcs_emotion_arc_html, tmp_path):
        """One file, not one per character: choosing a character is the point of the dropdown."""
        df = _frame(arcs_emotion_arc_html, n=300, characters=("Harry", "Ron", "Hermione"))
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Harry", "Ron", "Hermione"], str(tmp_path), "HPbooks")
        assert os.path.basename(out) == "emotion_arcs_HPbooks.html"
        data, _ = self._data(out)
        assert [c["name"] for c in data["chars"]] == ["Harry", "Ron", "Hermione"]

    def test_all_eight_emotions_are_selectable(self, arcs_emotion_arc_html, tmp_path):
        df = _frame(arcs_emotion_arc_html, n=200)
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Hermione"], str(tmp_path), "HPbooks")
        data, html = self._data(out)
        assert len(data["emotions"]) == 8
        assert "all eight" in html
        for e in arcs_emotion_arc_html.EIGHT_EMOTIONS:
            assert e.capitalize() in data["emotions"]
            assert data["colors"][e.capitalize()] == arcs_emotion_arc_html.NRC_COLORS[e]

    def test_the_file_carries_no_link_to_anything_outside_itself(self, arcs_emotion_arc_html, tmp_path):
        """It travels with the rest of the output and has to work on a machine with no internet."""
        df = _frame(arcs_emotion_arc_html, n=200)
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Hermione"], str(tmp_path), "HPbooks")
        _, html = self._data(out)
        for probe in ("http://", "https://", "<script src", "<link "):
            assert probe not in html, probe

    def test_the_numbers_in_the_file_match_the_frame(self, arcs_emotion_arc_html, tmp_path):
        df = _frame(arcs_emotion_arc_html, n=411)
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Hermione"], str(tmp_path), "HPbooks")
        data, _ = self._data(out)
        c = data["chars"][0]
        assert c["n"] == 411
        for e in arcs_emotion_arc_html.EIGHT_EMOTIONS:
            col = e.capitalize()
            weighted = sum(v * n for v, n in zip(c["series"][col], c["counts"])) / sum(c["counts"])
            assert weighted == pytest.approx(float(df[col].mean()), abs=5e-4)
            assert c["avg"][col] == pytest.approx(float(df[col].mean()), abs=5e-4)

    def test_the_peak_it_marks_is_the_real_peak(self, arcs_emotion_arc_html, tmp_path):
        df = _frame(arcs_emotion_arc_html, n=300)
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Hermione"], str(tmp_path), "HPbooks")
        data, _ = self._data(out)
        c = data["chars"][0]
        for col, peak in c["peaks"].items():
            assert peak["v"] == pytest.approx(max(c["series"][col]))
            assert c["series"][col][peak["i"]] == pytest.approx(peak["v"])

    def test_a_character_with_one_appearance_is_left_out(self, arcs_emotion_arc_html, pd, tmp_path):
        """One point is not an arc."""
        df = _frame(arcs_emotion_arc_html, n=200, characters=("Hermione",))
        df = pd.concat([df, pd.DataFrame([dict(df.iloc[0], Character="Ghost")])], ignore_index=True)
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Hermione", "Ghost"], str(tmp_path), "HPbooks")
        data, _ = self._data(out)
        assert [c["name"] for c in data["chars"]] == ["Hermione"]

    def test_no_characters_writes_nothing(self, arcs_emotion_arc_html, tmp_path):
        assert arcs_emotion_arc_html.emotion_arc_html(_frame(arcs_emotion_arc_html), [], str(tmp_path), "HPbooks") == ""
        assert not list(tmp_path.iterdir())

    def test_every_character_carries_its_position_in_the_corpus(self, arcs_emotion_arc_html, tmp_path):
        """Two characters' bin 60 are NOT the same moment - bins are cut over each character's own
        appearances, and Harry has three times as many as Hermione. Comparing them in narrative
        time needs a real position per bin, not a bin number."""
        df = _frame(arcs_emotion_arc_html, n=300, characters=("Harry", "Hermione"))
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Harry", "Hermione"], str(tmp_path), "HPbooks")
        data, _ = self._data(out)
        for c in data["chars"]:
            assert len(c["pos"]) == len(c["counts"])
            assert c["pos"] == sorted(c["pos"]), "positions must run forwards through the corpus"
        assert data["xmin"] <= min(c["pos"][0] for c in data["chars"])
        assert data["xmax"] >= max(c["pos"][-1] for c in data["chars"])

    def test_both_ways_of_lining_characters_up_are_offered(self, arcs_emotion_arc_html, tmp_path):
        """Own-appearances compares SHAPE; corpus position compares the same moment. The static
        PNG writes both readings, and dropping one here would quietly pick a side."""
        df = _frame(arcs_emotion_arc_html, n=200, characters=("Harry", "Ron"))
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Harry", "Ron"], str(tmp_path), "HPbooks")
        _, html = self._data(out)
        assert "each character's own arc" in html
        assert "position in the corpus" in html
        assert "needs ONE emotion" in html, "comparing must refuse all eight, and say why"

    def test_the_two_cautions_are_on_the_chart_not_only_in_the_TIPS(self, arcs_emotion_arc_html, tmp_path):
        """Both change what the arcs may be used to claim, and the person reading the chart is the
        person who needs them."""
        df = _frame(arcs_emotion_arc_html, n=200)
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Hermione"], str(tmp_path), "HPbooks")
        _, html = self._data(out)
        assert "sentence the character appears in" in html
        assert "tend to come out looking alike" in html

    def test_the_busiest_character_is_reduced_to_something_drawable(self, arcs_emotion_arc_html, tmp_path):
        """The whole point: 5,000 appearances x 8 emotions is 40,000 points in one chart."""
        df = _frame(arcs_emotion_arc_html, n=5000)
        out = arcs_emotion_arc_html.emotion_arc_html(df, ["Hermione"], str(tmp_path), "HPbooks")
        data, _ = self._data(out)
        c = data["chars"][0]
        assert c["n"] == 5000
        assert len(c["counts"]) == 120
        assert sum(len(s) for s in c["series"].values()) == 120 * 8
