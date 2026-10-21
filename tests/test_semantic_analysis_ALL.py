"""The Semantic analysis (ALL) GUI and its place in the NLP menu.

The GUI builds a Tk window at import, so its button list is read from the source (SEMANTIC_GUIS is a literal),
and the menu files are read as text: NLP_menu_main cannot be imported under the test stubs either.
"""

import ast
import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
GUI = "semantic_analysis_ALL_main.py"
LABEL = "Semantic analysis (ALL)"


def semantic_guis():
    tree = ast.parse((SRC / GUI).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "SEMANTIC_GUIS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("SEMANTIC_GUIS not found")


def test_every_button_opens_a_GUI_that_exists():
    guis = semantic_guis()
    assert guis
    for label, script in guis.items():
        assert script.endswith("_main.py"), label
        assert (SRC / script).is_file(), f"{label} -> {script} is missing"


def test_word_sense_induction_and_word_embeddings_are_reachable():
    # the reason for the GUI: WSI lives in semantic_analysis_main, which students could no longer find
    scripts = set(semantic_guis().values())
    assert "semantic_analysis_main.py" in scripts
    assert "WSI" in (SRC / "semantic_analysis_main.py").read_text(encoding="utf-8")
    assert "word2vec_main.py" in scripts


def test_each_button_has_its_help_text():
    source = (SRC / GUI).read_text(encoding="utf-8")
    for label in semantic_guis():
        assert f"Click on the '{label}' button" in source, label


def test_listed_in_the_menu_after_Syntactic_ALL_and_mapped_to_the_GUI():
    constants = (SRC / "constants_util.py").read_text(encoding="utf-8")
    assert f"'Syntactic analysis (ALL)', \\\n'{LABEL}'" in constants
    # "Semantic analysis (via TensorFlow)" had no tool behind it (its menu entry was dropped 1 Jul 2026)
    assert 'Semantic analysis (via TensorFlow)' not in constants
    menu = (SRC / "NLP_menu_main.py").read_text(encoding="utf-8")
    assert re.search(r'pydict\["Semantic analysis \(ALL\)"\] = \["semantic_analysis_ALL_main\.py", 1\]', menu)
    # nothing moved: the existing entries are still there
    assert 'pydict["Semantic analysis"] = ["semantic_analysis_main.py", 1]' in menu
    assert 'pydict["Word embeddings (Word2Vec) (via BERT & Gensim)"] = ["word2vec_main.py", 1]' in menu
