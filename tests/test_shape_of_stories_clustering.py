"""Shape of Stories, Hierarchical Clustering (#1722).

scikit-learn 1.4 removed AgglomerativeClustering(affinity=...), so every HC run ended in a TypeError
after the sentiment step, and SVD, NMF and best k (which come after HC in run()) never ran.

The first test needs nothing installed. The second runs the real clustering when scikit-learn is
installed (locally, not in CI).
"""

import importlib.util
import os
import sys
from unittest.mock import MagicMock, patch

import _real_pandas
import pytest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
_PATH = os.path.join(_SRC, "shape_of_stories_clustering_util.py")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, _PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_LOCAL_STUBS = {
    "shape_of_stories_vectorizer_util": MagicMock(),
    "shape_of_stories_visualization_util": MagicMock(),
}


def test_hc_does_not_pass_affinity():
    stubs = dict(_LOCAL_STUBS)
    for m in (
        "matplotlib",
        "matplotlib.pyplot",
        "scipy",
        "scipy.cluster",
        "scipy.cluster.hierarchy",
        "scipy.linalg",
        "sklearn",
        "sklearn.cluster",
        "sklearn.decomposition",
        "tqdm",
    ):
        if m not in sys.modules:
            stubs[m] = MagicMock()
    with patch.dict(sys.modules, stubs):
        mod = _load("_sos_clustering_stubbed")
    assert "affinity" not in mod.HC_PARAMS
    assert mod.HC_PARAMS["metric"] == "euclidean"


def test_hc_runs_on_real_scikit_learn():
    """The clustering and the dendrogram distances, on real scikit-learn (matplotlib stays stubbed)."""
    try:
        _, saved = _real_pandas.swap_in()
    except ImportError:
        pytest.skip("pandas/numpy not installed")
    try:
        # another test file may have left scikit-learn/scipy stubs behind: hide them while this runs
        with patch.dict(sys.modules):
            for m in [k for k, v in sys.modules.items() if k.split(".")[0] in ("sklearn", "scipy")]:
                if isinstance(sys.modules[m], MagicMock):
                    del sys.modules[m]
            try:
                import numpy as np
                from sklearn.cluster import AgglomerativeClustering
            except ImportError:
                pytest.skip("scikit-learn not installed")
            for m in ("matplotlib", "matplotlib.pyplot", "tqdm", *_LOCAL_STUBS):
                if m not in sys.modules or m in _LOCAL_STUBS:
                    sys.modules[m] = MagicMock()
            mod = _load("_sos_clustering_real")
            vectors = np.random.default_rng(0).random((8, 5))
            model = AgglomerativeClustering(n_clusters=3, **mod.HC_PARAMS)
            labels = model.fit_predict(vectors)
            assert len(set(labels)) == 3
            distances, weights = mod.Clustering(3).get_distances(vectors, model)
            assert len(distances) == len(vectors) - 1
            assert weights[-1] == len(vectors)
    finally:
        _real_pandas.swap_out(saved)


def test_nmf_input_is_shifted_to_nonnegative():
    """spaCy polarity (-1..1) stopped NMF with "Negative values in data passed to NMF initialization"."""
    try:
        _, saved = _real_pandas.swap_in()
    except ImportError:
        pytest.skip("pandas/numpy not installed")
    try:
        import numpy as np

        stubs = dict(_LOCAL_STUBS)
        for m in (
            "matplotlib",
            "matplotlib.pyplot",
            "scipy",
            "scipy.cluster",
            "scipy.cluster.hierarchy",
            "scipy.linalg",
            "sklearn",
            "sklearn.cluster",
            "sklearn.decomposition",
            "tqdm",
        ):
            if m not in sys.modules or m.startswith(("sklearn", "scipy")):
                stubs[m] = MagicMock()
        with patch.dict(sys.modules, stubs):
            mod = _load("_sos_clustering_nmf")
        shifted = mod.nonnegative([[-0.5, 0.25], [0.75, -1.0]])
        assert shifted.min() == 0
        assert np.allclose(shifted, [[0.5, 1.25], [1.75, 0.0]])
        assert np.allclose(mod.nonnegative([[1.0, 2.0]]), [[1.0, 2.0]])
    finally:
        _real_pandas.swap_out(saved)
