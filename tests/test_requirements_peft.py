"""requirements.txt lists peft, which Stanza's coreference model needs.

Stanza's coreference model is XLM-RoBERTa with LoRA adapters and loads them through peft, but stanza declares
peft only under its "transformers" extra, so `pip install stanza` leaves it out. The zip's python-env is built
from requirements.txt, and in 1.6.45 Coreference with Stanza stopped with "Failed to create the Stanza
coreference pipeline. No module named 'peft'" (found by tests/tool_sweep.py, recipe coreference_Stanza).
Nothing in src/ imports peft itself, so no import scan would notice if it were dropped again.
"""

import os
import re

REQUIREMENTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")


def _requirement_names(path):
    names = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                names.append(re.split(r"[\s\[<>=!~;]", line, maxsplit=1)[0].lower())
    return names


def test_requirements_list_peft_for_stanza_coreference():
    assert "peft" in _requirement_names(REQUIREMENTS)
