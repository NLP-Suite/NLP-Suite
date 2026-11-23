"""Self-update of the downloaded (zip) NLP Suite: picking the release zip, unpacking it, and the folder swap."""

import os
import pathlib
import shutil
import stat
import subprocess
import sys
import time
from unittest import mock
import zipfile

import pytest

import NLP_setup_self_update_util as su

REPO = pathlib.Path(__file__).resolve().parent.parent
posix_only = pytest.mark.skipif(os.name == "nt", reason="sh swap script and unix permissions")


# --- which install, which zip ---------------------------------------------------------------


def test_zip_install_is_the_frozen_app_or_its_python_env(tmp_path):
    assert su.is_zip_install(str(tmp_path), frozen=True)
    assert not su.is_zip_install(str(tmp_path), frozen=False)
    (tmp_path / "python-env").mkdir()
    assert su.is_zip_install(str(tmp_path), frozen=False)


def test_git_checkout_is_never_a_zip_install(tmp_path):
    (tmp_path / ".git").mkdir()
    assert not su.is_zip_install(str(tmp_path), frozen=True)


@pytest.mark.parametrize(
    ("plat", "machine", "expected"),
    [
        ("win32", "AMD64", "NLP-Suite-windows-x64.zip"),
        ("darwin", "arm64", "NLP-Suite-mac-arm64.zip"),
        ("darwin", "x86_64", None),  # no Intel Mac build
        ("linux", "x86_64", None),
        ("win32", "ARM64", None),
    ],
)
def test_asset_name(plat, machine, expected):
    assert su.asset_name(plat, machine) == expected


def test_asset_names_match_the_installer_workflow():
    workflow = (REPO / ".github" / "workflows" / "build-installers.yml").read_text(encoding="utf-8")
    for name in su.ASSET_NAMES.values():
        assert name in workflow


RELEASE = {
    "tag_name": "v1.6.41",
    "assets": [
        {
            "name": "NLP-Suite-mac-arm64.zip",
            "browser_download_url": "https://x/mac.zip",
            "size": 10,
            "state": "uploaded",
        },
        {"name": "NLP-Suite-windows-x64.zip", "browser_download_url": "https://x/win.zip", "size": 20},
    ],
}


def test_find_asset():
    assert su.find_asset(RELEASE, "NLP-Suite-windows-x64.zip", "1.6.41\n") == ("https://x/win.zip", 20)


def test_find_asset_waits_for_the_release_to_be_built():
    # current-stable says 1.6.42, but GitHub's latest release is still 1.6.41
    assert su.find_asset(RELEASE, "NLP-Suite-mac-arm64.zip", "1.6.42") is None


def test_find_asset_skips_a_half_uploaded_zip():
    release = {"tag_name": "v1.6.41", "assets": [dict(RELEASE["assets"][0], state="starter")]}
    assert su.find_asset(release, "NLP-Suite-mac-arm64.zip", "1.6.41") is None


def test_update_paths_sit_next_to_the_app(tmp_path):
    paths = su.update_paths(str(tmp_path / "NLP_Suite"))
    assert paths["stage"] == str(tmp_path / "NLP_Suite_update")
    assert paths["backup"] == str(tmp_path / "NLP_Suite_previous")


def test_claim_stage_is_a_lock_that_expires(tmp_path):
    stage = str(tmp_path / "stage")
    assert su.claim_stage(stage)
    assert not su.claim_stage(stage)
    assert su.claim_stage(stage, now=time.time() + su.STALE_STAGE_SECONDS + 60)


# --- download -----------------------------------------------------------------------------


def _fake_response(chunks):
    response = mock.MagicMock()
    response.__enter__.return_value = response
    response.iter_content.return_value = chunks
    return response


def test_download(tmp_path):
    dest = tmp_path / "a.zip"
    seen = []
    with mock.patch.object(sys.modules["requests"], "get", return_value=_fake_response([b"abc", b"de"])):
        assert su.download("u", str(dest), 5, on_progress=lambda d, t: seen.append(d))
    assert dest.read_bytes() == b"abcde"
    assert seen == [3, 5]


def test_download_rejects_an_incomplete_file(tmp_path):
    with mock.patch.object(sys.modules["requests"], "get", return_value=_fake_response([b"abc"])):
        with pytest.raises(OSError, match="incomplete"):
            su.download("u", str(tmp_path / "a.zip"), 5)


def test_download_can_be_cancelled(tmp_path):
    with mock.patch.object(sys.modules["requests"], "get", return_value=_fake_response([b"abc"])):
        assert su.download("u", str(tmp_path / "a.zip"), 3, cancelled=lambda: True) is False


# --- unpacking ----------------------------------------------------------------------------


def _entry(zf, name, data, mode):
    info = zipfile.ZipInfo(name)
    info.external_attr = mode << 16
    zf.writestr(info, data)


@posix_only
def test_extract_keeps_executable_bits_and_symlinks(tmp_path):
    archive = tmp_path / "r.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        _entry(zf, "NLP_Suite/NLP_Suite", b"#!/bin/sh\n", stat.S_IFREG | 0o755)
        _entry(zf, "NLP_Suite/python-env/bin/python3.10", b"bin", stat.S_IFREG | 0o755)
        _entry(zf, "NLP_Suite/python-env/bin/python3", b"python3.10", stat.S_IFLNK | 0o777)
        _entry(zf, "NLP_Suite/lib/release_version.txt", b"1.6.41", stat.S_IFREG | 0o644)
    out = tmp_path / "out"
    assert su.extract_zip(str(archive), str(out))
    assert os.access(out / "NLP_Suite" / "NLP_Suite", os.X_OK)
    link = out / "NLP_Suite" / "python-env" / "bin" / "python3"
    assert link.is_symlink() and os.readlink(link) == "python3.10"
    assert not os.access(out / "NLP_Suite" / "lib" / "release_version.txt", os.X_OK)
    assert su.unpacked_size(str(archive)) == len(b"#!/bin/sh\n") + 3 + len(b"python3.10") + 6


def test_extract_accepts_backslash_names(tmp_path):
    archive = tmp_path / "r.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("NLP_Suite\\lib\\release_version.txt", "1.6.41")
    su.extract_zip(str(archive), str(tmp_path / "out"))
    assert (tmp_path / "out" / "NLP_Suite" / "lib" / "release_version.txt").read_text() == "1.6.41"


@pytest.mark.parametrize("name", ["../evil.txt", "NLP_Suite/../../evil.txt", "/tmp/evil.txt"])
def test_extract_refuses_paths_outside_the_folder(tmp_path, name):
    archive = tmp_path / "r.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(name, "x")
    with pytest.raises(ValueError):
        su.extract_zip(str(archive), str(tmp_path / "out"))


def _fake_app(folder, version, exe="NLP_Suite"):
    (folder / "lib").mkdir(parents=True)
    (folder / "lib" / "release_version.txt").write_text(version + "\n")
    (folder / exe).write_text("app " + version)
    return folder


def test_staged_app_ok(tmp_path):
    staged = _fake_app(tmp_path / "NLP_Suite", "1.6.41")
    assert su.staged_app_ok(str(staged), "1.6.41\n", "darwin")
    assert not su.staged_app_ok(str(staged), "1.6.42", "darwin")
    assert not su.staged_app_ok(str(staged), "1.6.41", "win32")  # no NLP_Suite.exe


# --- the folder swap ----------------------------------------------------------------------


def _install(tmp_path, exe="NLP_Suite", edit_shipped=False):
    """An installed 1.6.40 (with its release file list) plus the user's settings, a folder of their own and a
    file of their own inside a shipped folder; a staged 1.6.41; and the carry list user_files() makes."""
    app = _fake_app(tmp_path / "NLP Suite's copy", "1.6.40", exe)
    (app / "lib" / "sampleData").mkdir()
    (app / "lib" / "sampleData" / "story.txt").write_text("shipped story")
    su.write_manifest(str(app))  # the build writes it last, before zipping
    (app / "lib" / "sampleData" / "mine.txt").write_text("my own sample")
    if edit_shipped:
        (app / "lib" / "sampleData" / "story.txt").write_text("my edited story")
    (app / "config").mkdir()
    (app / "config" / "NLP_default_IO_config.csv").write_text("my folders")
    (app / "reminders").mkdir()
    (app / "reminders" / "reminders.csv").write_text("my reminders")
    (app / "my corpus").mkdir()
    (app / "my corpus" / "doc.txt").write_text("mine")
    paths = su.update_paths(str(app))
    os.mkdir(paths["stage"])
    new = _fake_app(pathlib.Path(paths["stage"]) / su.APP_FOLDER_IN_ZIP, "1.6.41", exe)
    (new / "lib" / "sampleData").mkdir()
    (new / "lib" / "sampleData" / "story.txt").write_text("shipped story, 1.6.41")
    (new / "config").mkdir()
    (new / "config" / "NLP_default_IO_config.csv").write_text("defaults")
    (new / "config" / "new_setting.csv").write_text("new")
    carry, changed, complete = su.user_files(str(app), str(new))
    su.write_carry_list(paths["stage"], carry)
    return app, paths, complete


def _run_posix_swap(tmp_path, paths, new=None, keep_backup=False):
    log = tmp_path / "update.log"
    script = tmp_path / "update.sh"
    new = new or os.path.join(paths["stage"], su.APP_FOLDER_IN_ZIP)
    script.write_text(
        su.posix_swap_script(paths["app"], new, paths["backup"], paths["stage"], "1.6.41", str(log), keep_backup)
    )
    env = dict(os.environ, NLP_SUITE_UPDATE_QUIET="1")
    result = subprocess.run(["/bin/sh", str(script)], env=env, timeout=60)
    return result.returncode, log.read_text()


@posix_only
def test_posix_swap_installs_the_new_release_and_keeps_user_files(tmp_path):
    app, paths, _ = _install(tmp_path)
    code, log = _run_posix_swap(tmp_path, paths)
    assert code == 0, log
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.41"
    assert (app / "config" / "NLP_default_IO_config.csv").read_text() == "my folders"
    assert (app / "config" / "new_setting.csv").read_text() == "new"
    assert (app / "reminders" / "reminders.csv").read_text() == "my reminders"
    assert (app / "my corpus" / "doc.txt").read_text() == "mine"
    assert (app / "lib" / "sampleData" / "mine.txt").read_text() == "my own sample"
    assert (app / "lib" / "sampleData" / "story.txt").read_text() == "shipped story, 1.6.41"
    backup = pathlib.Path(paths["backup"])
    assert (backup / "lib" / "release_version.txt").read_text().strip() == "1.6.40"
    assert (backup / su.BACKUP_MARKER).is_file()
    assert not os.path.exists(paths["stage"])


@posix_only
def test_posix_swap_replaces_an_older_backup(tmp_path):
    app, paths, _ = _install(tmp_path)
    _fake_app(pathlib.Path(paths["backup"]), "1.6.39")
    (pathlib.Path(paths["backup"]) / su.BACKUP_MARKER).write_text("done")
    code, log = _run_posix_swap(tmp_path, paths)
    assert code == 0, log
    assert (pathlib.Path(paths["backup"]) / "lib" / "release_version.txt").read_text().strip() == "1.6.40"


@posix_only
def test_posix_swap_never_deletes_an_unmarked_previous_folder(tmp_path):
    app, paths, _ = _install(tmp_path)
    theirs = pathlib.Path(paths["backup"])
    theirs.mkdir()
    (theirs / "thesis.docx").write_text("not ours to delete")
    code, log = _run_posix_swap(tmp_path, paths)
    assert code == 1
    assert "in the way" in log
    assert (theirs / "thesis.docx").read_text() == "not ours to delete"
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.40"


@posix_only
def test_posix_swap_keeps_the_backup_when_the_user_edited_a_release_file(tmp_path):
    app, paths, complete = _install(tmp_path, edit_shipped=True)
    assert not complete
    code, log = _run_posix_swap(tmp_path, paths, keep_backup=True)
    assert code == 0, log
    backup = pathlib.Path(paths["backup"])
    assert (backup / "lib" / "sampleData" / "story.txt").read_text() == "my edited story"
    assert not (backup / su.BACKUP_MARKER).exists()
    assert (app / "lib" / "sampleData" / "mine.txt").read_text() == "my own sample"


@posix_only
def test_posix_swap_puts_the_old_version_back_when_it_fails(tmp_path):
    app, paths, _ = _install(tmp_path)
    code, log = _run_posix_swap(tmp_path, paths, new=os.path.join(paths["stage"], "missing"))
    assert code == 1
    assert "FAILED" in log
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.40"
    assert (app / "config" / "NLP_default_IO_config.csv").read_text() == "my folders"
    assert not os.path.exists(paths["stage"])


POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


windows_only = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None, reason="runs the PowerShell swap script on Windows"
)


def _run_windows_swap(tmp_path, paths, keep_backup=False):
    log = tmp_path / "update.log"
    script = tmp_path / "update.ps1"
    new = os.path.join(paths["stage"], su.APP_FOLDER_IN_ZIP)
    text = su.windows_swap_script(paths["app"], new, paths["backup"], paths["stage"], "1.6.41", str(log), keep_backup)
    script.write_text(text, encoding="utf-8-sig")
    env = dict(os.environ, NLP_SUITE_UPDATE_QUIET="1")
    command = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    result = subprocess.run(command, env=env, timeout=180)
    return result.returncode, log.read_text(encoding="utf-8", errors="ignore")


@windows_only
def test_windows_swap_installs_the_new_release_and_keeps_user_files(tmp_path):
    app, paths, complete = _install(tmp_path, exe="NLP_Suite.exe")
    assert complete
    code, log = _run_windows_swap(tmp_path, paths)
    assert code == 0, log
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.41"
    assert (app / "config" / "NLP_default_IO_config.csv").read_text() == "my folders"
    assert (app / "config" / "new_setting.csv").read_text() == "new"
    assert (app / "reminders" / "reminders.csv").read_text() == "my reminders"
    assert (app / "my corpus" / "doc.txt").read_text() == "mine"
    assert (app / "lib" / "sampleData" / "mine.txt").read_text() == "my own sample"
    assert (app / "lib" / "sampleData" / "story.txt").read_text() == "shipped story, 1.6.41"
    assert (pathlib.Path(paths["backup"]) / su.BACKUP_MARKER).is_file()
    assert not os.path.exists(paths["stage"])


@windows_only
def test_windows_swap_never_deletes_an_unmarked_previous_folder(tmp_path):
    app, paths, _ = _install(tmp_path, exe="NLP_Suite.exe")
    theirs = pathlib.Path(paths["backup"])
    theirs.mkdir()
    (theirs / "thesis.docx").write_text("not ours to delete")
    code, log = _run_windows_swap(tmp_path, paths)
    assert code == 1
    assert "in the way" in log
    assert (theirs / "thesis.docx").read_text() == "not ours to delete"
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.40"


@windows_only
def test_windows_swap_replaces_a_marked_backup(tmp_path):
    app, paths, _ = _install(tmp_path, exe="NLP_Suite.exe")
    _fake_app(pathlib.Path(paths["backup"]), "1.6.39")
    (pathlib.Path(paths["backup"]) / su.BACKUP_MARKER).write_text("done")
    code, log = _run_windows_swap(tmp_path, paths)
    assert code == 0, log
    assert (pathlib.Path(paths["backup"]) / "lib" / "release_version.txt").read_text().strip() == "1.6.40"


@windows_only
def test_windows_swap_keeps_the_backup_when_the_user_edited_a_release_file(tmp_path):
    app, paths, complete = _install(tmp_path, exe="NLP_Suite.exe", edit_shipped=True)
    assert not complete
    code, log = _run_windows_swap(tmp_path, paths, keep_backup=True)
    assert code == 0, log
    backup = pathlib.Path(paths["backup"])
    assert (backup / "lib" / "sampleData" / "story.txt").read_text() == "my edited story"
    assert not (backup / su.BACKUP_MARKER).exists()
    assert (app / "lib" / "sampleData" / "mine.txt").read_text() == "my own sample"


@windows_only
def test_windows_swap_runs_in_a_folder_with_a_curly_apostrophe(tmp_path):
    root = tmp_path / "Maria’s files [2026]"  # typographic apostrophe, and brackets (PowerShell wildcards)
    root.mkdir()
    app, paths, _ = _install(root, exe="NLP_Suite.exe")
    code, log = _run_windows_swap(tmp_path, paths)
    assert code == 0, log
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.41"
    assert (app / "lib" / "sampleData" / "mine.txt").read_text() == "my own sample"


def test_windows_swap_script_quotes_paths():
    script = su.windows_swap_script(
        r"C:\Users\O'Neil\NLP_Suite", r"C:\x\new", r"C:\x\old", r"C:\x\stage", "1.6.41", r"C:\t\log"
    )
    assert r"$App = 'C:\Users\O''Neil\NLP_Suite'" in script
    assert "$PID" not in script  # read-only automatic variable in PowerShell


def test_write_swap_script_goes_to_the_temp_folder(tmp_path):
    paths = su.update_paths(str(tmp_path / "NLP_Suite"))
    with mock.patch.object(su.tempfile, "gettempdir", return_value=str(tmp_path / "tmp")):
        os.mkdir(tmp_path / "tmp")
        script, log = su.write_swap_script(paths, "1.6.41", "win32")
    assert script.endswith(".ps1") and os.path.dirname(script) == str(tmp_path / "tmp")
    assert pathlib.Path(script).read_bytes().startswith(b"\xef\xbb\xbf")  # BOM for Windows PowerShell 5.1
    assert log == str(tmp_path / "tmp" / "NLP_Suite_update.log")


# --- deleting the backup once the new version starts ----------------------------------------


def _backup(tmp_path, marked):
    app = tmp_path / "NLP_Suite"
    app.mkdir()
    backup = _fake_app(pathlib.Path(su.update_paths(str(app))["backup"]), "1.6.40")
    (backup / "python-env" / "bin").mkdir(parents=True)
    (backup / "python-env" / "bin" / "python3").write_text("x")
    if marked:
        (backup / su.BACKUP_MARKER).write_text("done")
    return app, backup


def test_marked_backup_is_deleted(tmp_path):
    app, backup = _backup(tmp_path, marked=True)
    su.remove_previous_version(str(app), background=False)
    assert not backup.exists()
    assert app.exists()


def test_marked_backup_is_deleted_in_the_background(tmp_path):
    app, backup = _backup(tmp_path, marked=True)
    thread = su.remove_previous_version(str(app))
    assert thread is not None
    thread.join(timeout=30)
    assert not backup.exists()


def test_unmarked_backup_is_kept(tmp_path):
    # the swap script did not finish carrying the user's files over, or the folder is not ours
    app, backup = _backup(tmp_path, marked=False)
    assert su.remove_previous_version(str(app)) is None
    assert (backup / "lib" / "release_version.txt").exists()


def test_no_backup_is_fine(tmp_path):
    assert su.remove_previous_version(str(tmp_path / "NLP_Suite")) is None


# --- what the student is told -------------------------------------------------------------


def test_no_download_reason_names_the_computer():
    reason = su.no_download_reason("darwin", "x86_64")
    assert "x86_64" in reason and "Apple chips" in reason


@pytest.mark.parametrize(
    ("done", "total", "elapsed", "expected"),
    [
        (100, 1000, 1, ""),  # too early to tell
        (0, 1000, 10, ""),
        (1000, 1000, 10, ""),  # finished
        (500, 1000, 20, "less than a minute left"),
        (100, 1000, 10, "about 2 minutes left"),  # 90 s
        (300, 1400, 60, "about 4 minutes left"),  # 220 s
        (900, 1000, 540, "about 1 minute left"),
    ],
)
def test_time_left(done, total, elapsed, expected):
    assert su.time_left(done, total, elapsed) == expected


# --- the user's own files (release file list) ----------------------------------------------------


def test_write_manifest_skips_caches_symlinks_and_itself(tmp_path):
    app = _fake_app(tmp_path / "NLP_Suite", "1.6.41")
    (app / "src" / "__pycache__").mkdir(parents=True)
    (app / "src" / "__pycache__" / "x.cpython-310.pyc").write_bytes(b"x")
    (app / "src" / "tool.py").write_text("print(1)")
    assert su.write_manifest(str(app)) == 3  # release_version.txt, NLP_Suite, src/tool.py
    rows = su.read_manifest(str(app))
    assert set(rows) == {"lib/release_version.txt", "NLP_Suite", "src/tool.py"}
    assert rows["src/tool.py"][0] == len("print(1)")
    assert rows["src/tool.py"][1]  # small files are hashed


def test_user_files_finds_additions_at_any_depth_and_edits(tmp_path):
    old = _fake_app(tmp_path / "old", "1.6.41")
    (old / "lib" / "wordLists").mkdir()
    (old / "lib" / "wordLists" / "stop.txt").write_text("a\nthe\n")
    (old / "lib" / "wordLists" / "same_size.txt").write_text("abc")
    su.write_manifest(str(old))
    (old / "lib" / "wordLists" / "my_list.txt").write_text("mine")  # added inside a shipped folder
    (old / "output").mkdir()
    (old / "output" / "run.csv").write_text("mine")  # added at the top
    (old / "lib" / "wordLists" / "same_size.txt").write_text("xyz")  # edited, same size: caught by the hash
    (old / "config").mkdir()
    (old / "config" / "IO.csv").write_text("settings are carried separately")
    (old / "src" / "__pycache__").mkdir(parents=True)
    (old / "src" / "__pycache__" / "a.pyc").write_bytes(b"x")
    new = _fake_app(tmp_path / "new", "1.6.42")
    carry, changed, complete = su.user_files(str(old), str(new))
    assert carry == ["lib/wordLists/my_list.txt", "output/run.csv"]
    assert changed == ["lib/wordLists/same_size.txt"]
    assert not complete


def test_user_files_without_a_file_list_keeps_the_backup(tmp_path):
    old = _fake_app(tmp_path / "old", "1.6.40")
    (old / "my corpus").mkdir()
    (old / "config").mkdir()
    new = _fake_app(tmp_path / "new", "1.6.41")
    carry, changed, complete = su.user_files(str(old), str(new))
    assert carry == ["my corpus"]
    assert changed == []
    assert not complete  # cannot tell edits apart: the backup must not be deleted


def test_backup_blocker_only_for_an_unmarked_folder(tmp_path):
    backup = tmp_path / "NLP_Suite_previous"
    assert su.backup_blocker(str(backup)) == ""
    backup.mkdir()
    assert "in the way" in su.backup_blocker(str(backup))
    (backup / su.BACKUP_MARKER).write_text("done")
    assert su.backup_blocker(str(backup)) == ""


def test_onedrive_folder(tmp_path):
    root = tmp_path / "OneDrive - Emory"
    env = {"OneDriveCommercial": str(root)}
    assert su.onedrive_folder(str(root / "Documents" / "NLP_Suite"), env) == str(root)
    assert su.onedrive_folder(str(tmp_path / "OneDrive - Emory2" / "NLP_Suite"), env) == ""
    assert su.onedrive_folder(str(tmp_path / "NLP_Suite"), {}) == ""


def test_ps_quote_doubles_every_kind_of_single_quote():
    assert su._ps_quote("Maria\u2019s") == "'Maria\u2019\u2019s'"
    assert su._ps_quote("O'Neil") == "'O''Neil'"


def test_partial_backup_deletion_keeps_the_marker(tmp_path):
    backup = tmp_path / "NLP_Suite_previous"
    (backup / "lib").mkdir(parents=True)
    (backup / su.BACKUP_MARKER).write_text("done")
    with mock.patch.object(su.shutil, "rmtree"):  # e.g. a locked file: the folder survives
        su._delete_backup(str(backup))
    assert (backup / su.BACKUP_MARKER).is_file()  # so the next start tries again
    su._delete_backup(str(backup))
    assert not backup.exists()


def test_swap_script_started(tmp_path):
    assert not su.swap_script_started(str(tmp_path), timeout=0.2, poll=0.05)
    (tmp_path / su.STARTED_FLAG).write_text("")
    assert su.swap_script_started(str(tmp_path), timeout=0.2, poll=0.05)


def test_outdated_message_says_what_this_install_does():
    zip_msg = su.outdated_message("1.6.40\n", "1.6.41\n", zip_install=True)
    assert "1.6.40" in zip_msg and "1.6.41" in zip_msg
    assert "close the NLP Suite" in zip_msg
    assert "git-scm" not in zip_msg  # the downloaded build never needs Git
    git_msg = su.outdated_message("1.6.40", "1.6.41", zip_install=False)
    assert "git-scm.com" in git_msg and su.RELEASES_URL in git_msg


def test_release_download_ready_checks_the_download_link():
    class R:
        def __init__(self, code):
            self.status_code = code

    with mock.patch.object(su, "asset_name", return_value="NLP-Suite-windows-x64.zip"):
        with mock.patch("requests.head", return_value=R(302)) as head:
            assert su.release_download_ready("1.6.41\n")
        assert head.call_args[0][0].endswith("/download/v1.6.41/NLP-Suite-windows-x64.zip")
        with mock.patch("requests.head", return_value=R(404)):
            assert not su.release_download_ready("1.6.41")
    with mock.patch.object(su, "asset_name", return_value=None):
        assert not su.release_download_ready("1.6.41")


@windows_only
def test_launch_swap_script_really_runs_powershell(tmp_path):
    # The swap tests above start PowerShell directly. This goes through launch_swap_script, as the app does:
    # started with DETACHED_PROCESS, Windows PowerShell exited at once without running the script, and a real
    # update stopped with "the program that installs the new version did not start".
    flag = tmp_path / su.STARTED_FLAG
    script = tmp_path / "probe.ps1"
    script.write_text("[System.IO.File]::WriteAllText('" + str(flag) + "', '')\n", encoding="utf-8-sig")
    su.launch_swap_script(str(script), "win32")
    assert su.swap_script_started(str(tmp_path), timeout=30)
