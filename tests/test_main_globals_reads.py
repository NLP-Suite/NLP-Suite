"""Every ``globals()["X"]`` read in a GUI's run() names a variable the GUI defines at module level.

run() reads its widgets' variables with ``globals()["X"].get()``. Ruff's F821 cannot see a name inside a string, so a
read of a variable the GUI never creates passes lint and raises KeyError on every RUN: Syntactic analysis read
``globals()["WSI_keywords_var"]`` and ``globals()["WSIdictionary_file_var"]``, copied from Semantic analysis, and RUN
failed before any option ran (found 23 Nov 2026; tool_sweep recipe syntactic_WSD).
"""

import ast
import glob
import os

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
MAINS = sorted(glob.glob(os.path.join(SRC, "*_main.py")))


def _module_level_names(tree):
    names = set()
    for node in ast.walk(tree):
        # anywhere in the module: a global statement inside a function also defines a module-level name
        if isinstance(node, ast.Global):
            names.update(node.names)
    for node in tree.body:
        for sub in ast.walk(node) if not isinstance(node, (ast.FunctionDef, ast.ClassDef)) else [node]:
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                names.add(sub.id)
            elif isinstance(sub, (ast.FunctionDef, ast.ClassDef)):
                names.add(sub.name)
            elif isinstance(sub, (ast.Import, ast.ImportFrom)):
                names.update((a.asname or a.name).split(".")[0] for a in sub.names)
    return names


def _globals_reads(tree):
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "globals"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
            and isinstance(node.ctx, ast.Load)
        ):
            yield node.slice.value, node.lineno


@pytest.mark.parametrize("path", MAINS, ids=os.path.basename)
def test_globals_reads_name_module_variables(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        tree = ast.parse(f.read().replace("\r\n", "\n").replace("\r", "\n"))
    defined = _module_level_names(tree)
    missing = [f"{name} (line {line})" for name, line in _globals_reads(tree) if name not in defined]
    assert missing == [], f"{os.path.basename(path)} reads globals() names it never defines: {missing}"
