"""Every module.function a src/ module calls on another src/ module exists there.

ruff's F821 sees undefined names, not missing attributes: sentence_analysis_util.extract_sentences (#1760) and
BERT_util.spell_checker_bert (#1762) had been removed, and the GUIs that called them stopped with AttributeError.
This parses src/ (no imports, so no Tk and no NLP libraries) and lists `mod.name` uses where mod is an imported
src/ module whose top level defines no `name`.
"""

import ast
import glob
import os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")

# Left as they are, with the reason. Shrink this list; never grow it for new code.
KNOWN = {
    "data_visualization_main.py: charts_util.comparative_bar_charts": "#1779",
    "DB_PCACE_data_analysis_main.py: charts_util.timechart": "#1779",
    "IO_files_util.py: reminders_util.generate_reminder_list": "#1779",
    # guarded by hasattr(GUI_IO_util, "outputDirPath")
    "language_tools_advisor_util.py: GUI_IO_util.outputDirPath": "guarded",
}


def _parse(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return ast.parse(f.read())


def _top_level_names(tree):
    names = set()
    for node in ast.walk(tree):  # anything a module can bind, also inside functions (global x; x = ...)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                names |= {n.id for n in ast.walk(target) if isinstance(n, ast.Name)}
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names |= {(a.asname or a.name).split(".")[0] for a in node.names}
        elif isinstance(node, ast.Global):
            names.update(node.names)
    return names


def missing_attributes():
    paths = {os.path.basename(p)[:-3]: p for p in glob.glob(os.path.join(SRC, "*.py"))}
    trees = {}
    for name, path in paths.items():
        try:
            trees[name] = _parse(path)
        except SyntaxError:
            continue
    defined = {name: _top_level_names(tree) for name, tree in trees.items()}
    found = set()
    for name, tree in trees.items():
        aliases = {
            a.asname or a.name: a.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for a in node.names
            if a.name in defined
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in aliases:
                if node.attr not in defined[aliases[node.value.id]]:
                    found.add(f"{name}.py: {node.value.id}.{node.attr}")
    return found


def test_called_functions_exist():
    assert sorted(missing_attributes() - set(KNOWN)) == []


def test_known_list_has_no_stale_entries():
    assert sorted(set(KNOWN) - missing_attributes()) == []
