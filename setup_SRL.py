#!/usr/bin/env python
"""One-time setup for the NLP Suite's Semantic Role Labeling (SRL) feature.

SRL runs in a SEPARATE, isolated Python 3.8 environment because transformer-srl pins a legacy stack
(torch 1.7, allennlp 1.2, spaCy 2.x) that cannot coexist with the Suite's modern packages. This is
the same idea as CoreNLP running in its own Java runtime.

Run this ONCE per machine. It:
  1. creates a conda env named 'nlp_srl' (Python 3.8),
  2. installs the pinned SRL dependencies into it (in the order that resolves cleanly),
  3. downloads the pretrained SRL model into lib/SRL/.

Usage:    python setup_SRL.py
Requires: conda on PATH (Anaconda/Miniconda) and an internet connection.
After it finishes, tick the SRL checkbox in the SVO GUI.
"""

import os
import subprocess
import urllib.request
from shutil import which

ENV_NAME = "nlp_srl"
PY_VERSION = "3.8"
MODEL_URL = "https://www.dropbox.com/s/4tes6ypf2do0feb/srl_bert_base_conll2012.tar.gz?dl=1"
MODEL_NAME = "srl_bert_base_conll2012.tar.gz"

# Pinned deps, split into two pip steps because protobuf/overrides must be pinned DOWN after the
# main install pulls newer versions (this is the sequence verified to run on a modern machine).
PIP_STEP1 = ["setuptools", "numpy<2", "transformer-srl==2.4.6"]
PIP_STEP2 = ["overrides<7", "protobuf<3.21"]
SPACY_MODEL = "en_core_web_sm"

SUITE_ROOT = os.path.dirname(os.path.abspath(__file__))
LIB_SRL = os.path.join(SUITE_ROOT, "lib", "SRL")


def run(cmd):
    print(">>> " + " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit("Command failed (exit %d): %s" % (r.returncode, " ".join(cmd)))


def env_python():
    """Path to the created env's python (cross-platform)."""
    base = subprocess.check_output(["conda", "info", "--base"]).decode().strip()
    win = os.path.join(base, "envs", ENV_NAME, "python.exe")
    nix = os.path.join(base, "envs", ENV_NAME, "bin", "python")
    return win if os.path.isfile(win) else nix


def main():
    if which("conda") is None:
        raise SystemExit("conda was not found on PATH. Install Anaconda/Miniconda, then re-run.")

    print("=== 1/3  Creating conda env '%s' (Python %s) ===" % (ENV_NAME, PY_VERSION))
    run(["conda", "create", "-n", ENV_NAME, "python=" + PY_VERSION, "-y"])

    py = env_python()
    print("=== 2/3  Installing pinned SRL dependencies (this pulls torch 1.7, allennlp, spaCy 2) ===")
    run([py, "-m", "pip", "install"] + PIP_STEP1)
    run([py, "-m", "pip", "install"] + PIP_STEP2)
    run([py, "-m", "spacy", "download", SPACY_MODEL])

    print("=== 3/3  Downloading SRL model (~400 MB) ===")
    os.makedirs(LIB_SRL, exist_ok=True)
    dest = os.path.join(LIB_SRL, MODEL_NAME)
    if os.path.isfile(dest):
        print("Model already present: " + dest)
    else:
        print("Downloading to " + dest + " ...")
        urllib.request.urlretrieve(MODEL_URL, dest)
        print("Downloaded.")

    print("\n[OK] SRL setup complete. Tick the SRL checkbox in the SVO GUI to use it.")


if __name__ == "__main__":
    main()
