"""Word2Vec charts: four readable views instead of one bar per word pair (Roberto, 21 Oct 2026: "The chart output is
unreadable and pretty useless. There must be a better way of visualizing this").

The logic is plain Python on (word_1, word_2, value) rows. The drawing (Plotly) is checked only where the real
Plotly is importable: conftest may stub it.
"""

import csv
import importlib.util

import word2vec_charts_util as wc

# two clear groups: animals close to each other, fruit close to each other, far across groups
COS = [
    ("cat", "dog", 0.9),
    ("apple", "pear", 0.8),
    ("cat", "apple", 0.1),
    ("cat", "pear", 0.2),
    ("dog", "apple", 0.15),
    ("dog", "pear", 0.1),
]
EUC = [(a, b, 1 - v) for a, b, v in COS]  # a distance: smaller = closer


def test_histogram_counts_every_pair_in_range():
    bins = wc.histogram_bins([0.0, 0.1, 0.5, 1.0], n_bins=4)
    assert len(bins) == 4 and sum(n for _a, _b, n in bins) == 4
    assert bins[0][0] == 0.0 and bins[-1][1] == 1.0 and bins[-1][2] == 1  # the top edge falls in the last bin
    assert wc.histogram_bins([0.5, 0.5]) == [(0.5, 0.5, 2)]
    assert wc.histogram_bins([]) == []


def test_closest_pairs_respects_the_direction_of_the_measure():
    assert wc.closest_pairs(COS, True, 2) == [("cat", "dog", 0.9), ("apple", "pear", 0.8)]
    assert [r[:2] for r in wc.closest_pairs(EUC, False, 2)] == [("cat", "dog"), ("apple", "pear")]


def test_nearest_neighbours_of_each_word():
    nn = wc.nearest_neighbours(COS, True, k=1)
    assert nn["cat"] == [("dog", 0.9)] and nn["pear"] == [("apple", 0.8)]
    assert wc.nearest_neighbours(EUC, False, k=1)["dog"][0][0] == "cat"


def test_cluster_order_keeps_each_group_together():
    for rows, larger in ((COS, True), (EUC, False)):
        order = wc.cluster_order(rows, larger)
        assert sorted(order) == ["apple", "cat", "dog", "pear"]
        pos = {w: i for i, w in enumerate(order)}
        assert abs(pos["cat"] - pos["dog"]) == 1 and abs(pos["apple"] - pos["pear"]) == 1


def test_matrix_is_symmetric_with_an_empty_diagonal():
    m = wc.matrix(["cat", "dog"], COS)
    assert m == [[None, 0.9], [0.9, None]]


def test_neighbours_csv(tmp_path):
    path = wc.write_neighbours_csv(
        str(tmp_path / "nn.csv"), wc.nearest_neighbours(COS, True, k=2), "Cosine similarity", k=2
    )
    rows = list(csv.reader(open(path, encoding="utf-8")))
    assert rows[0] == ["Word", "Neighbour 1", "Cosine similarity 1", "Neighbour 2", "Cosine similarity 2"]
    assert ["cat", "dog", "0.9", "pear", "0.2"] in rows


def test_charts_write_the_four_files(tmp_path):
    import pytest
    import _real_pandas

    if importlib.util.find_spec("plotly") is None:
        pytest.skip("Plotly not installed here")
    try:
        _pandas, saved = _real_pandas.swap_in()  # Plotly needs the real numpy, not conftest's stub
    except ImportError:
        pytest.skip("real numpy/pandas not installed here")
    try:
        files = wc.charts(COS, "Cosine similarity", True, lambda part, ext: str(tmp_path / (part + ext)))
    finally:
        _real_pandas.swap_out(saved)
    assert [f.rsplit("/", 1)[-1].rsplit("\\", 1)[-1] for f in files] == [
        "hist.html",
        "closest.html",
        "heatmap.html",
        "neighbours.csv",
    ]
    assert all((tmp_path / n).stat().st_size > 0 for n in ("hist.html", "closest.html", "heatmap.html"))
