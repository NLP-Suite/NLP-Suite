"""Every call in src/ to a file_spell_checker_util function passes arguments its signature accepts (#1762).

The spell checker GUI called nltk_unusual_words with 10 positional arguments (it takes 6 to 8): TypeError, and with
"*" none of the other checkers ran either. The calls are read with ast across src/ and bound to the signatures read
from file_spell_checker_util's source (it imports nltk, stanza, langdetect... which CI does not install).
"""

import ast
import glob
import inspect
import os

import pytest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
MODULE = "file_spell_checker_util"


def _signatures():
    source = open(os.path.join(SRC, MODULE + ".py"), encoding="utf-8-sig").read()
    signatures = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef):
            node.body = [ast.Pass()]
            node.decorator_list = []
            node.returns = None
            args = node.args
            for a in args.posonlyargs + args.args + args.kwonlyargs:
                a.annotation = None
            # only the shape of the signature matters: defaults may name things the module imports
            args.defaults = [ast.Constant(None) for _ in args.defaults]
            args.kw_defaults = [None if d is None else ast.Constant(None) for d in args.kw_defaults]
            namespace = {}
            exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), "f", "exec"), namespace)
            signatures[node.name] = inspect.signature(namespace[node.name])
    return signatures


def _calls():
    for path in sorted(glob.glob(os.path.join(SRC, "*.py"))):
        for n in ast.walk(ast.parse(open(path, encoding="utf-8-sig").read())):
            if (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name)
                and n.func.value.id == MODULE
                and not any(isinstance(a, ast.Starred) for a in n.args)
            ):
                yield pytest.param(n, id=f"{os.path.basename(path)}:{n.lineno}:{n.func.attr}")


SIGNATURES = _signatures()


@pytest.mark.parametrize("call", list(_calls()))
def test_call_binds_to_the_signature(call):
    assert call.func.attr in SIGNATURES, f"{MODULE} has no function {call.func.attr}"
    SIGNATURES[call.func.attr].bind(*range(len(call.args)), **{k.arg: None for k in call.keywords if k.arg})


def test_the_spell_checker_gui_calls_nltk_unusual_words():
    assert any("file_spell_checker_main" in p.id and "nltk_unusual_words" in p.id for p in _calls())
