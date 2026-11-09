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


def _install(tmp_path):
    """An installed 1.6.40 with user settings and a user folder, and a staged 1.6.41."""
    app = _fake_app(tmp_path / "NLP Suite's copy", "1.6.40")
    (app / "config").mkdir()
    (app / "config" / "NLP_default_IO_config.csv").write_text("my folders")
    (app / "reminders").mkdir()
    (app / "reminders" / "reminders.csv").write_text("my reminders")
    (app / "my corpus").mkdir()
    (app / "my corpus" / "doc.txt").write_text("mine")
    paths = su.update_paths(str(app))
    os.mkdir(paths["stage"])
    new = _fake_app(pathlib.Path(paths["stage"]) / su.APP_FOLDER_IN_ZIP, "1.6.41")
    (new / "config").mkdir()
    (new / "config" / "NLP_default_IO_config.csv").write_text("defaults")
    (new / "config" / "new_setting.csv").write_text("new")
    return app, paths


def _run_posix_swap(tmp_path, paths, new=None):
    log = tmp_path / "update.log"
    script = tmp_path / "update.sh"
    new = new or os.path.join(paths["stage"], su.APP_FOLDER_IN_ZIP)
    script.write_text(su.posix_swap_script(paths["app"], new, paths["backup"], paths["stage"], "1.6.41", str(log)))
    env = dict(os.environ, NLP_SUITE_UPDATE_QUIET="1")
    result = subprocess.run(["/bin/sh", str(script)], env=env, timeout=60)
    return result.returncode, log.read_text()


@posix_only
def test_posix_swap_installs_the_new_release_and_keeps_user_files(tmp_path):
    app, paths = _install(tmp_path)
    code, log = _run_posix_swap(tmp_path, paths)
    assert code == 0, log
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.41"
    assert (app / "config" / "NLP_default_IO_config.csv").read_text() == "my folders"
    assert (app / "config" / "new_setting.csv").read_text() == "new"
    assert (app / "reminders" / "reminders.csv").read_text() == "my reminders"
    assert (app / "my corpus" / "doc.txt").read_text() == "mine"
    backup = pathlib.Path(paths["backup"])
    assert (backup / "lib" / "release_version.txt").read_text().strip() == "1.6.40"
    assert (backup / su.BACKUP_MARKER).is_file()
    assert not os.path.exists(paths["stage"])


@posix_only
def test_posix_swap_replaces_an_older_backup(tmp_path):
    app, paths = _install(tmp_path)
    _fake_app(pathlib.Path(paths["backup"]), "1.6.39")
    code, log = _run_posix_swap(tmp_path, paths)
    assert code == 0, log
    assert (pathlib.Path(paths["backup"]) / "lib" / "release_version.txt").read_text().strip() == "1.6.40"


@posix_only
def test_posix_swap_puts_the_old_version_back_when_it_fails(tmp_path):
    app, paths = _install(tmp_path)
    code, log = _run_posix_swap(tmp_path, paths, new=os.path.join(paths["stage"], "missing"))
    assert code == 1
    assert "FAILED" in log
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.40"
    assert (app / "config" / "NLP_default_IO_config.csv").read_text() == "my folders"
    assert not os.path.exists(paths["stage"])


POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


@pytest.mark.skipif(os.name != "nt" or POWERSHELL is None, reason="runs the PowerShell swap script on Windows")
def test_windows_swap_installs_the_new_release_and_keeps_user_files(tmp_path):
    app, paths = _install(tmp_path)
    for folder in (app, pathlib.Path(paths["stage"]) / su.APP_FOLDER_IN_ZIP):
        (folder / "NLP_Suite").rename(folder / "NLP_Suite.exe")
    log = tmp_path / "update.log"
    script = tmp_path / "update.ps1"
    new = os.path.join(paths["stage"], su.APP_FOLDER_IN_ZIP)
    text = su.windows_swap_script(paths["app"], new, paths["backup"], paths["stage"], "1.6.41", str(log))
    script.write_text(text, encoding="utf-8-sig")
    env = dict(os.environ, NLP_SUITE_UPDATE_QUIET="1")
    command = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    result = subprocess.run(command, env=env, timeout=120)
    assert result.returncode == 0, log.read_text(errors="ignore")
    assert (app / "lib" / "release_version.txt").read_text().strip() == "1.6.41"
    assert (app / "config" / "NLP_default_IO_config.csv").read_text() == "my folders"
    assert (app / "config" / "new_setting.csv").read_text() == "new"
    assert (app / "reminders" / "reminders.csv").read_text() == "my reminders"
    assert (app / "my corpus" / "doc.txt").read_text() == "mine"
    assert (pathlib.Path(paths["backup"]) / su.BACKUP_MARKER).is_file()
    assert not os.path.exists(paths["stage"])


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
