"""Every script that src/ launches by name with run_script_util must exist, with that exact case.

run_script joins the name onto the src folder and checks os.path.isfile, which ignores case on the
default Windows and Mac disks but not on Linux or a case-sensitive APFS volume. "Word2Vec_main.py"
(the file is word2vec_main.py) opened there only by luck.
"""

import os
import re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")

LAUNCH = re.compile(r"run_script(?:_detached)?\(\s*[\"']([^\"']+\.py)[\"']")

# Known, not fixed here: docs/future-work.md §5.1 #12 (corpus_checker_PCACE_data_main launches a
# WordNet.py that does not exist). Remove the entry when that launcher is fixed.
KNOWN_MISSING = {("corpus_checker_PCACE_data_main.py", "WordNet.py")}


def _launches():
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(SRC, name), encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                for match in LAUNCH.finditer(line):
                    yield name, lineno, match.group(1)


def test_finds_launches():
    assert sum(1 for _ in _launches()) > 20


def test_every_launched_script_exists_with_exact_case():
    files = set(os.listdir(SRC))
    missing = [
        f"{caller}:{lineno} launches {target}"
        for caller, lineno, target in _launches()
        if target not in files and (caller, target) not in KNOWN_MISSING
    ]
    assert not missing, "\n".join(missing)


def test_known_missing_is_still_missing():
    files = set(os.listdir(SRC))
    launched = {(caller, target) for caller, _, target in _launches()}
    for caller, target in KNOWN_MISSING:
        assert (caller, target) in launched and target not in files, (
            f"{caller} → {target} is fixed: remove it from KNOWN_MISSING"
        )
