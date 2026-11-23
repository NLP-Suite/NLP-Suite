"""SVO: the Sankey chart runs on pandas 2, and the '*' (all parsers) option calls run() the way run() is defined.

Sankey: in pandas 2, value_counts().reset_index() names its columns [var, 'count'], not ['index', var]. The old rename
then turned var itself into 'Frequency', and the next line raised KeyError: 'Verb (V)'. Every SVO run reaches the
3-way Sankey, so lemmatizing, filtering, WordNet, the maps and the network graphs never ran.

charts_util imports the GUI and every plotting library, so only the Sankey function is pulled out of the source and run
against the real pandas, with Plotly mocked so the figure's input can be read back.

'*': the run()/lambda sweep (b4b5c1c6) changed run() to read its widgets itself and take no arguments, but the '*'
branch still called it with 26, so it raised TypeError: run() takes 0 positional arguments but 26 were given.
"""

import ast
import os
from unittest.mock import MagicMock

import _real_pandas
import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def _function_source(filename, name):
    source = open(os.path.join(SRC, filename), encoding="utf-8-sig").read()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, node)


@pytest.fixture(scope="module")
def sankey():
    try:
        pd, saved = _real_pandas.swap_in()
    except ImportError as exc:
        pytest.skip(f"real pandas not available: {exc}")
    import numpy as np

    go = MagicMock()
    namespace = {"pd": pd, "np": np, "go": go, "mb": MagicMock()}
    exec(_function_source("charts_util.py", "Sankey"), namespace)
    yield namespace["Sankey"], go, pd
    _real_pandas.swap_out(saved)


def test_three_way_sankey_counts_each_link(sankey, tmp_path):
    Sankey, go, pd = sankey
    go.reset_mock()
    data = pd.DataFrame(
        {
            "Subject (S)": ["police", "police", "police", "mayor"],
            "Verb (V)": ["arrest", "arrest", "say", "say"],
            "Object (O)": ["man", "man", "it", "it"],
        }
    )
    out = str(tmp_path / "sankey.html")
    assert Sankey(data, out, "Subject (S)", 10, "Verb (V)", 10, True, "Object (O)", 10) == out

    link = go.Sankey.call_args.kwargs["link"]
    labels = go.Sankey.call_args.kwargs["node"]["label"]
    assert labels == ["mayor", "police", "arrest", "say", "it", "man"]
    flows = {
        (labels[s], labels[t]): v for s, t, v in zip(link["source"], link["target"], link["value"], strict=False) if v
    }
    assert flows == {
        ("mayor", "say"): 1,
        ("police", "arrest"): 2,
        ("police", "say"): 1,
        ("arrest", "man"): 2,
        ("say", "it"): 2,
    }


def _run_signature(tree):
    run = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run"), None)
    if run is None:
        return None
    a = run.args
    return [p.arg for p in a.posonlyargs + a.args], {p.arg for p in a.args + a.kwonlyargs}, a.vararg, a.kwarg


@pytest.mark.parametrize("filename", sorted(f for f in os.listdir(SRC) if f.endswith("_main.py")))
def test_calls_to_run_match_its_definition(filename):
    tree = ast.parse(open(os.path.join(SRC, filename), encoding="utf-8-sig").read())
    signature = _run_signature(tree)
    if signature is None:
        return
    positional, named, vararg, kwarg = signature
    for call in ast.walk(tree):
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "run"):
            continue
        where = f"{filename}:{call.lineno}"
        assert vararg or len(call.args) <= len(positional), where
        assert kwarg or all(k.arg in named for k in call.keywords), where


def test_all_parsers_option_finds_each_parsers_svo_csv(tmp_path):
    namespace = {"os": os}
    exec(_function_source("SVO_main.py", "main_SVO_csv"), namespace)
    main_SVO_csv = namespace["main_SVO_csv"]

    svo_dir = tmp_path / "SVO_spaCy_doc"
    for rel in (
        "SVO_CoNLL/NLP_CoNLL_SpaCy_doc.csv",
        "SVO_CoNLL/NLP_SVO_spaCy_doc.csv",
        "SVO_CoNLL/sunburst_treemap_intermediate.csv",
        "SVO_filter/NLP_SVO_filter_SV_spaCy_doc.csv",
        "SVO_lemma/NLP_SVO_lemma_spaCy_doc.csv",
        "GIS/NLP_SVO_spaCy_LOCATIONS_doc.csv",
    ):
        (svo_dir / rel).parent.mkdir(parents=True, exist_ok=True)
        (svo_dir / rel).write_text("")
    assert main_SVO_csv(str(svo_dir)) == str(svo_dir / "SVO_CoNLL" / "NLP_SVO_spaCy_doc.csv")
    assert main_SVO_csv(str(tmp_path / "missing")) == ""
