"""No module selects the Tk backend for matplotlib.

The zip's python-env (python-build-standalone) has no working TkAgg, and matplotlib.use("TkAgg") does not
fail when called, only at the first figure: MALLET topic modeling crashed this way in 1.6.45. The Suite saves
charts to files, so Agg is all it needs.
"""

import glob
import os
import re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")


def test_no_module_selects_tkagg():
    offenders = []
    for path in glob.glob(os.path.join(SRC, "*.py")):
        with open(path, encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                code = line.split("#", 1)[0]
                if re.search(r"""\.use\(\s*["']TkAgg["']""", code, re.IGNORECASE):
                    offenders.append(f"{os.path.basename(path)}:{n}")
    assert offenders == []
