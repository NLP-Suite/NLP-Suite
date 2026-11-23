"""Every SVOWordCloud call in src/ matches its signature.

SVO_main's csv-input branch called SVOWordCloud(myfile, inputFilename, tempOutputDir, wordcloud_title,
prefer_horizontal=0.9). With transformed_image_mask left out, the title went into its slot and the call raised
TypeError: SVOWordCloud() missing 1 required positional argument: 'wordcloud_title', so an SVO csv given as input
never got its wordcloud. SVO_main is a GUI module, so the calls are read from the source rather than run.
"""

import ast
import inspect
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"


def _signature():
    tree = ast.parse((SRC / "wordclouds_util.py").read_text(encoding="utf-8"))
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "SVOWordCloud")
    namespace = {}
    exec(compile(ast.Module(body=[func], type_ignores=[]), "wordclouds_util.py", "exec"), namespace)
    return inspect.signature(namespace["SVOWordCloud"])


def _calls():
    for path in sorted(SRC.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                if name == "SVOWordCloud":
                    yield f"{path.name}:{node.lineno}", node


def test_every_call_binds():
    signature = _signature()
    calls = list(_calls())
    assert calls, "no SVOWordCloud calls found"
    for where, call in calls:
        args = [None] * len(call.args)
        kwargs = {k.arg: None for k in call.keywords}
        try:
            bound = signature.bind(*args, **kwargs)
        except TypeError as e:
            raise AssertionError(f"{where}: {e}") from None
        assert "wordcloud_title" in bound.arguments, where
