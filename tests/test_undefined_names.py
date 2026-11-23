"""No undefined names in src/: ruff F821 (undefined name) and F823 (local used before assignment).

Each such name raises NameError when its line runs, and pre-commit lints only the files a commit touches, so old
modules were never checked: on 23 Nov 2026 `ruff check src --select F821,F823` found 44, among them
charts_Excel_main.py (every Excel chart that succeeded ended in NameError: startTime) and GIS_Google_Earth_main.py
(italic_var_list used before assignment). This test lints all of src/ so a new one fails CI.

CI installs ruff for it (.github/workflows/tests.yml). Locally the test is skipped when ruff is neither importable
nor on PATH.
"""

import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files whose hits are left as they are, with the reason. Shrink this list; never grow it for new code.
KNOWN = {
    # dead files that PR #1706 deletes
    "html_annotator_extractor_util_NEW.py": "deleted by PR #1706",
    "nyt_api_call.py": "deleted by PR #1706",
    # its 6 are fixed on fix/syntactic-analysis-run; remove this line when both have merged
    "syntactic_analysis_ALL_main.py": "fixed on fix/syntactic-analysis-run",
}


def _ruff():
    try:
        import ruff  # noqa: F401  (the PyPI package ships the binary and a module that finds it)

        return [sys.executable, "-m", "ruff"]
    except ImportError:
        exe = shutil.which("ruff")
        return [exe] if exe else None


def test_no_undefined_names_in_src():
    ruff = _ruff()
    if ruff is None:
        pytest.skip("ruff is not installed (CI installs it)")
    result = subprocess.run(
        ruff + ["check", "src", "--select", "F821,F823", "--output-format", "json", "--no-cache", "--isolated"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode in (0, 1), result.stderr
    hits = [
        f"{os.path.relpath(h['filename'], ROOT)}:{h['location']['row']} {h['message']}"
        for h in json.loads(result.stdout or "[]")
        if os.path.basename(h["filename"]) not in KNOWN
    ]
    assert hits == [], "undefined names in src/:\n" + "\n".join(hits)
