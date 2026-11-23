"""No call to IO_files_util.generate_output_file_name has an extension where a folder belongs.

Its arguments are (inputFilename, inputDir, outputDir, outputExtension, labels...). A call that left out
inputDir, as Semantic aggregation's "Aggregate by sentence index" did (#1780), passes the output folder as
inputDir and ".csv" as outputDir, and pandas then stops with "Cannot save file into a non-existent directory:
'.csv'". This parses src/ (no imports) and lists calls with a ".xyz" string in the inputDir or outputDir slot.
"""

import ast
import glob
import os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
KNOWN = {"html_annotator_extractor_util_NEW.py"}  # dead file, deleted by PR #1706


def shifted_calls():
    found = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.py"))):
        if os.path.basename(path) in KNOWN:
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if name != "generate_output_file_name":
                continue
            for slot in (1, 2):  # inputDir, outputDir
                arg = node.args[slot] if len(node.args) > slot else None
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("."):
                    found.append(f"{os.path.basename(path)}:{node.lineno}")
    return found


def test_no_extension_in_a_folder_argument():
    assert shifted_calls() == []
