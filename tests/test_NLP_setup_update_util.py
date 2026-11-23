"""Auto-update must not depend on pygit2, and must not try git on the installer build.

Most students run the prebuilt installer (no Python, no pygit2, no .git folder) or a source
install that never got pygit2. Before this fix both hit "pygit2 is not available" on every exit.
"""

import os
import shutil
import subprocess
import sys
from unittest import mock

import pytest

import NLP_setup_update_util as upd


def test_module_does_not_import_pygit2():
    assert "pygit2" not in sys.modules or not hasattr(upd, "Repository")
    assert not hasattr(upd, "_has_pygit2")


def test_installer_build_uses_download_page(tmp_path):
    (tmp_path / ".git").mkdir()
    assert upd.update_method(str(tmp_path), frozen=True) == "download"


def test_folder_without_git_uses_download_page(tmp_path):
    assert upd.update_method(str(tmp_path), frozen=False) == "download"


def test_git_checkout_without_git_program_asks_for_git(tmp_path):
    (tmp_path / ".git").mkdir()
    with mock.patch.object(upd.shutil, "which", return_value=None):
        assert upd.update_method(str(tmp_path), frozen=False) == "install_git"


def test_git_checkout_with_git_program_uses_git(tmp_path):
    (tmp_path / ".git").mkdir()
    with mock.patch.object(upd.shutil, "which", return_value="/usr/bin/git"):
        assert upd.update_method(str(tmp_path), frozen=False) == "git"


@pytest.mark.skipif(shutil.which("git") is None, reason="needs the git program")
def test_current_git_branch_reads_branch_without_pygit2(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "current-stable", str(tmp_path)], check=True)
    env = dict(
        os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t"
    )
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "--allow-empty", "-m", "x"], check=True, env=env)
    assert upd.current_git_branch(str(tmp_path)) == "current-stable"


@pytest.mark.skipif(shutil.which("git") is None, reason="needs the git program")
def test_current_git_branch_returns_none_outside_a_repo(tmp_path):
    with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(tmp_path.parent)}):
        assert upd.current_git_branch(str(tmp_path)) is None


@pytest.mark.parametrize(
    ("local", "remote", "expected"),
    [
        ("1.6.40\n", "1.6.41\n", True),
        ("1.6.40", "1.6.40\n", False),
        ("1.6.40", "0.0.0", False),  # offline
        ("1.6.41", "1.6.40", False),  # developer copy ahead of GitHub
        ("1.6.9", "1.6.10", True),
        ("1.6.40", "404: Not Found", False),
    ],
)
def test_newer_release_available(local, remote, expected):
    assert upd.newer_release_available(local, remote) is expected


@pytest.mark.parametrize(
    ("error", "damaged"),
    [
        ("fatal: not a git repository (or any of the parent directories): .git", True),
        ("error: object file .git/objects/ab/cd is empty\nfatal: loose object abcd is corrupt", True),
        ("fatal: detected dubious ownership in repository at 'C:/NLP-Suite'", False),
        ("fatal: Unable to create '.git/index.lock': File exists.", False),
        ("Could not run git: timed out", False),
        ("", False),
    ],
)
def test_git_folder_is_damaged_only_for_real_damage(error, damaged):
    # deleting .git on any other error would wipe a working checkout (e.g. a lab machine where the folder
    # belongs to another account and git refuses it as "dubious ownership")
    assert upd.git_folder_is_damaged(error) is damaged


@pytest.mark.skipif(shutil.which("git") is None, reason="needs the git program")
def test_read_git_branch_returns_gits_error_outside_a_repo(tmp_path):
    with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(tmp_path.parent)}):
        branch, error = upd.read_git_branch(str(tmp_path))
    assert branch is None
    assert "not a git repository" in error.lower()
