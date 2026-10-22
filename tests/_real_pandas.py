"""Swap the REAL pandas (and numpy) in for conftest's stubs, importing them only once per test run.

conftest stubs pandas and numpy for every test. A few test files need the real libraries for a while
and then put the stubs back. Each used to import them afresh, but numpy cannot be imported twice in
one process: the second copy breaks the first, whose functions then fail with errors such as
"int() argument must be ... not '_NoValueType'". So whichever file ran second failed, but only where
pandas is installed (locally, not in CI). Here the real modules are imported once and cached, and
every later swap puts the same objects back.
"""

import sys

_ROOTS = ("pandas", "numpy")
_REAL = {}  # module name -> the real module, filled on the first successful swap


def _ours(name):
    return name.split(".")[0] in _ROOTS


def swap_in():
    """Put the real pandas/numpy into sys.modules. Returns (pandas, saved stubs).

    Raises ImportError (stubs already restored) when the real pandas is not installed.
    """
    saved = {k: v for k, v in sys.modules.items() if _ours(k)}
    for k in saved:
        del sys.modules[k]
    sys.modules.update(_REAL)
    try:
        import pandas

        if not hasattr(pandas, "DataFrame") or list(pandas.DataFrame({"a": [1]}).columns) != ["a"]:
            raise ImportError("pandas resolved to the stub, not the real library")
    except Exception as exc:
        swap_out(saved)
        raise ImportError(str(exc)) from exc
    return pandas, saved


def swap_out(saved):
    """Put conftest's stubs back, keeping the real modules (including lazily loaded ones) for next time."""
    real = {k: v for k, v in sys.modules.items() if _ours(k)}
    _REAL.update(real)
    for k in real:
        del sys.modules[k]
    sys.modules.update(saved)
