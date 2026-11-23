"""Nothing under config/ is tracked by git.

config/ holds each user's own settings and counters. build-installers.yml copies config/ into the release
when the checkout has one, so a tracked file there ships to every new install: a committed
config/launch_count.json ({"count": 12}) would have made every new install skip the welcome screen, which
shows on the first three launches. First-run defaults belong in lib/config_defaults/.
"""

import os
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_no_tracked_files_in_config():
    if shutil.which("git") is None or not os.path.exists(os.path.join(ROOT, ".git")):
        pytest.skip("not a git checkout")
    tracked = subprocess.run(
        ["git", "ls-files", "config"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    assert tracked == [], "move first-run defaults to lib/config_defaults/"
