"""Self-update for the downloaded (zip) NLP Suite.

The zip build is not a git checkout, so git cannot update it. When a newer release is out,
update_zip_install() downloads that release's zip for this computer, unpacks it next to the
NLP Suite folder, and starts a small script that swaps the two folders once every NLP Suite
window is closed. Windows cannot rename a folder while a program inside it is running, which is
why the swap happens in a separate script and not in this process.

The user's settings (config/ and reminders/) and anything they added to the NLP Suite folder are
carried over. The old folder is kept next to the new one as <folder>_previous and deleted the first
time the new version starts (remove_previous_version, called by NLP_menu_main).
"""

# This module reports progress to the terminal, during exit, after the GUI window is gone.
# ruff: noqa: T201

import hashlib
import math
import os
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import zipfile

RELEASE_API_URL = "https://api.github.com/repos/NLP-Suite/NLP-Suite/releases/latest"
RELEASES_URL = "https://github.com/NLP-Suite/NLP-Suite/releases/latest"
# Must match the artifact names in .github/workflows/build-installers.yml (a test checks this).
ASSET_NAMES = {
    ("win32", "x64"): "NLP-Suite-windows-x64.zip",
    ("darwin", "arm64"): "NLP-Suite-mac-arm64.zip",
}
APP_FOLDER_IN_ZIP = "NLP_Suite"
KEEP_FROM_OLD = ("config", "reminders")
# Written into the backup by the swap script, only after everything the user added was carried over.
# The backup is deleted only when this file is there, so a folder we did not finish with is never deleted.
BACKUP_MARKER = "NLP_Suite_previous_version.txt"
STALE_STAGE_SECONDS = 24 * 3600
WAIT_FOR_CLOSE_SECONDS = 3600
# The release's own file list (path, size, hash), written by the build (build-installers.yml) just before
# zipping. Comparing the installed folder against it tells the user's own files -- added anywhere, or
# shipped files they edited, e.g. in lib/sampleData -- from the release's, so nothing of theirs is lost.
MANIFEST = "lib/release_manifest.tsv"
HASH_LIMIT = 16 << 20  # files above this are compared by size only (models, DLLs: nobody edits them)
CARRY_LIST = "carry.txt"  # in the staging folder: the user's files the swap script moves into the new version
STARTED_FLAG = "started"  # written by the swap script as its first act, so the app knows it is running


def is_zip_install(NLPPath, frozen=None):
    """True for the downloaded build: the PyInstaller app, or a tool it started on its bundled python-env."""
    if os.path.isdir(os.path.join(NLPPath, ".git")):
        return False
    if frozen is None:
        frozen = getattr(sys, "frozen", False)
    return bool(frozen) or os.path.isdir(os.path.join(NLPPath, "python-env"))


def asset_name(sys_platform=None, machine=None):
    """Name of the release zip for this computer, or None when no zip is built for it (e.g. Intel Macs)."""
    sys_platform = sys_platform or sys.platform
    machine = (machine or platform.machine()).lower()
    if machine in ("amd64", "x86_64"):
        arch = "x64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        return None
    return ASSET_NAMES.get((sys_platform, arch))


def no_download_reason(sys_platform=None, machine=None):
    """Why there is no release zip for this computer (only asked when asset_name() is None)."""
    sys_platform = sys_platform or sys.platform
    machine = machine or platform.machine()
    return (
        "no NLP Suite download is built for this computer ("
        + sys_platform
        + ", "
        + machine
        + "). Downloads are built for 64-bit Windows and for Macs with Apple chips (M1 or later)."
    )


def time_left(done, total, elapsed):
    """'about 3 minutes left', from the speed so far; '' for the first few seconds, while the speed settles."""
    if done <= 0 or total <= done or elapsed < 3:
        return ""
    seconds = elapsed * (total - done) / done
    if seconds < 60:
        return "less than a minute left"
    minutes = math.ceil(seconds / 60)
    return "about " + str(minutes) + (" minute" if minutes == 1 else " minutes") + " left"


def version_number(text):
    return str(text).strip().lstrip("vV")


def find_asset(release, name, expected_version):
    """(download url, size in bytes) of the zip `name` in a GitHub release, or None.

    Also None when the release is not `expected_version`: right after a release is tagged,
    current-stable already reports the new version, but its zips take a while to build.
    """
    if version_number(release.get("tag_name", "")) != version_number(expected_version):
        return None
    for asset in release.get("assets", []):
        if asset.get("name") == name and asset.get("state", "uploaded") == "uploaded":
            return asset["browser_download_url"], int(asset["size"])
    return None


def update_paths(NLPPath):
    """The NLP Suite folder, the staging folder the new release is unpacked into, and the backup folder.

    Staging and backup sit next to the NLP Suite folder, on the same disk, so the swap is a rename.
    """
    app = os.path.normpath(os.path.abspath(NLPPath))
    parent, base = os.path.split(app)
    return {
        "app": app,
        "stage": os.path.join(parent, base + "_update"),
        "backup": os.path.join(parent, base + "_previous"),
    }


def claim_stage(stage, now=None):
    """Create the staging folder; False if another update is already using it.

    A staging folder older than a day is left over from a failed update: it is removed and claimed.
    Raises OSError (e.g. PermissionError) when the folder cannot be created at all.
    """
    now = time.time() if now is None else now
    if os.path.isdir(stage) and now - os.path.getmtime(stage) > STALE_STAGE_SECONDS:
        shutil.rmtree(stage, ignore_errors=True)
    try:
        os.mkdir(stage)
    except FileExistsError:
        return False
    return True


def backup_blocker(backup):
    """Why an existing <folder>_previous stops the update, or '' when there is none or it is ours to replace.

    Only a backup the swap script marked complete may be deleted. An unmarked one is either a backup kept
    on purpose (files of the user's were not carried over) or a folder of the user's that has that name.
    """
    if not os.path.exists(backup):
        return ""
    if os.path.isfile(os.path.join(backup, BACKUP_MARKER)):
        return ""
    return (
        "a folder named\n\n"
        + backup
        + "\n\nis in the way. It may be the previous NLP Suite version, kept because some of your files were not "
        "carried over to the new one, or a folder of yours. Copy anything you need out of it, then delete or rename "
        "it, and close the NLP Suite again."
    )


def _release_files(root):
    """(relative path with '/', full path) of every regular file under root; no symlinks, no Python caches."""
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not os.path.islink(os.path.join(folder, d))]
        for name in files:
            path = os.path.join(folder, name)
            if name.endswith(".pyc") or os.path.islink(path):
                continue
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if rel != MANIFEST:
                yield rel, path


def _file_hash(path, size):
    if size > HASH_LIMIT:
        return ""
    h = hashlib.blake2b(digest_size=16)
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_manifest(app_dir):
    """Write the release's file list into app_dir (called by the build). Returns the number of files."""
    lines = []
    for rel, path in _release_files(app_dir):
        size = os.path.getsize(path)
        lines.append(rel + "\t" + str(size) + "\t" + _file_hash(path, size))
    lines.sort()
    with open(os.path.join(app_dir, MANIFEST), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return len(lines)


def read_manifest(app_dir):
    """{relative path: (size, hash)} from the installed release's file list, or None if it has none."""
    try:
        with open(os.path.join(app_dir, MANIFEST), encoding="utf-8") as f:
            rows = [line.rstrip("\n").split("\t") for line in f if line.strip()]
    except OSError:
        return None
    return {r[0]: (int(r[1]), r[2] if len(r) > 2 else "") for r in rows if len(r) >= 2 and r[1].isdigit()}


def user_files(old_app, new_app):
    """The user's own files in the installed NLP Suite, compared with the release it came from.

    Returns (carry, changed, complete):
      carry    relative paths ('/') the user added anywhere, which the new release does not ship: moved over;
      changed  release files the user edited (or added ones the new release also ships): they cannot be
               moved without overwriting the new release, so they stay in the backup;
      complete True when the backup holds nothing of the user's, so it may be deleted.
    config/ and reminders/ are carried separately (KEEP_FROM_OLD) and left out. Without a file list
    (a release built before 1.6.41) only top-level additions can be told apart, and the backup is kept.
    """
    manifest = read_manifest(old_app)
    keep = tuple(k + "/" for k in KEEP_FROM_OLD)
    carry, changed = [], []
    if manifest is None:
        for name in sorted(os.listdir(old_app)):
            if name not in KEEP_FROM_OLD and not os.path.lexists(os.path.join(new_app, name)):
                carry.append(name)
        return carry, changed, False
    for rel, path in _release_files(old_app):
        if rel.startswith(keep):
            continue
        shipped = manifest.get(rel)
        if shipped is None:
            (changed if os.path.lexists(os.path.join(new_app, rel)) else carry).append(rel)
            continue
        size = os.path.getsize(path)
        if size != shipped[0] or (shipped[1] and _file_hash(path, size) != shipped[1]):
            changed.append(rel)
    return sorted(carry), sorted(changed), not changed


def write_carry_list(stage, carry):
    with open(os.path.join(stage, CARRY_LIST), "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(rel + "\n" for rel in carry))


def onedrive_folder(path, environ=None):
    """The OneDrive folder that holds path, or '' (Windows sets these variables for each OneDrive account)."""
    environ = os.environ if environ is None else environ
    full = os.path.normcase(os.path.abspath(path))
    for var in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        root = environ.get(var, "")
        if root and (full + os.sep).startswith(os.path.normcase(os.path.abspath(root)) + os.sep):
            return root
    return ""


def download(url, dest, expected_size, on_progress=None, cancelled=lambda: False):
    """Stream url to dest. Returns False if cancelled; raises OSError if the download is incomplete."""
    import requests

    done = 0
    with requests.get(url, stream=True, timeout=30) as response:
        response.raise_for_status()
        with open(dest, "wb") as out:
            for chunk in response.iter_content(1 << 20):
                if cancelled():
                    return False
                out.write(chunk)
                done += len(chunk)
                if on_progress:
                    on_progress(done, expected_size)
    if done != expected_size:
        raise OSError(f"the download is incomplete ({done} of {expected_size} bytes).")
    return True


def unpacked_size(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        return sum(info.file_size for info in zf.infolist())


def extract_zip(zip_path, dest, on_progress=None, cancelled=lambda: False):
    """Unzip, keeping the Mac build's executable bits and symlinks, which zipfile.extractall drops.

    Without them the Mac app and its python-env cannot start. Returns False if cancelled.
    """
    dest = os.path.abspath(dest)
    with zipfile.ZipFile(zip_path) as zf:
        members = zf.infolist()
        for i, info in enumerate(members):
            if cancelled():
                return False
            # Windows' Compress-Archive may write backslashes
            name = info.filename.replace("\\", "/")
            target = os.path.normpath(os.path.join(dest, name))
            if os.path.isabs(name) or os.path.commonpath([dest, target]) != dest:
                raise ValueError("the zip contains a path outside its folder: " + info.filename)
            mode = info.external_attr >> 16
            if name.endswith("/"):
                os.makedirs(target, exist_ok=True)
            elif os.name != "nt" and stat.S_ISLNK(mode):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if os.path.lexists(target):
                    os.remove(target)
                os.symlink(zf.read(info).decode("utf-8"), target)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with zf.open(info) as source, open(target, "wb") as out:
                    shutil.copyfileobj(source, out, 1 << 20)
                if os.name != "nt" and mode & 0o777:
                    os.chmod(target, mode & 0o777)
            if on_progress:
                on_progress(i + 1, len(members))
    return True


def staged_app_ok(staged_app, expected_version, sys_platform=None):
    """The unpacked folder has the app and is the version we meant to install."""
    sys_platform = sys_platform or sys.platform
    exe = "NLP_Suite.exe" if sys_platform == "win32" else "NLP_Suite"
    version_file = os.path.join(staged_app, "lib", "release_version.txt")
    if not (os.path.isfile(os.path.join(staged_app, exe)) and os.path.isfile(version_file)):
        return False
    with open(version_file, encoding="utf-8", errors="ignore") as f:
        return version_number(f.read()) == version_number(expected_version)


def posix_swap_script(app, new, backup, stage, version, log, keep_backup=False):  # noqa: PLR0917
    """sh script (Mac) that swaps in the new release once no NLP Suite program is running."""
    q = shlex.quote
    keep = " ".join(KEEP_FROM_OLD)
    return f"""#!/bin/sh
# NLP Suite updater, written by NLP_setup_self_update_util.py. Safe to delete.
APP={q(app)}
NEW={q(new)}
OLD={q(backup)}
STAGE={q(stage)}
VERSION={q(version)}
LOG={q(log)}
KEEP_BACKUP={1 if keep_backup else 0}
exec >>"$LOG" 2>&1
: > "$STAGE/{STARTED_FLAG}"
echo "$(date): updating the NLP Suite in $APP to $VERSION"

tell() {{
    [ -n "$NLP_SUITE_UPDATE_QUIET" ] && return 0  # set by the tests
    osascript -e 'on run argv' -e 'display dialog (item 1 of argv) with title "NLP Suite update" buttons {{"OK"}} default button 1' -e 'end run' "$1" >/dev/null 2>&1 || true
}}

fail() {{
    echo "FAILED: $1"
    rm -rf "$STAGE"
    tell "The NLP Suite could not be updated to $VERSION: $1

Your current version still works. Details are in $LOG"
    exit 1
}}

# Wait until no program from the NLP Suite folder is running. The menu is started as ./NLP_Suite,
# without its folder, so it is also looked for by name.
waited=0
while :; do
    ps ax -o command= > "$STAGE/processes.txt" 2>/dev/null
    if ! grep -F -q -- "$APP/" "$STAGE/processes.txt" && ! pgrep -x NLP_Suite >/dev/null 2>&1; then
        break
    fi
    [ "$waited" -ge {WAIT_FOR_CLOSE_SECONDS} ] && fail "NLP Suite windows were still open after an hour."
    sleep 2
    waited=$((waited + 2))
done

# only a backup this updater marked complete may be deleted; anything else there is the user's
if [ -e "$OLD" ] || [ -L "$OLD" ]; then
    [ -f "$OLD/{BACKUP_MARKER}" ] || fail "a folder named $OLD is in the way and was not deleted. Copy what you need out of it, delete or rename it, and close the NLP Suite again."
    rm -rf "$OLD"
    [ -e "$OLD" ] && fail "could not remove the old backup $OLD."
fi
mv "$APP" "$OLD" || fail "could not move $APP aside."
if ! mv "$NEW" "$APP"; then
    if mv "$OLD" "$APP"; then
        fail "could not move the new version into place."
    fi
    echo "FAILED: could not move the new version into place, nor the old one back."
    tell "The NLP Suite could not be updated to $VERSION, and its folder could not be put back.

Your NLP Suite is now in $OLD. Rename that folder back to $APP to use it. Details are in $LOG"
    exit 1
fi

# keep the user's settings
carried=1
for d in {keep}; do
    if [ -d "$OLD/$d" ]; then
        {{ mkdir -p "$APP/$d" && cp -Rp "$OLD/$d/." "$APP/$d/"; }} || carried=0
    fi
done
# move over the user's own files (listed by user_files: added anywhere, not shipped by the new release)
if [ -f "$STAGE/{CARRY_LIST}" ]; then
    while IFS= read -r rel || [ -n "$rel" ]; do
        [ -n "$rel" ] || continue
        [ -e "$OLD/$rel" ] || [ -L "$OLD/$rel" ] || continue
        if [ -e "$APP/$rel" ]; then
            echo "Not moved, the new version has it too: $rel"
            carried=0
            continue
        fi
        {{ mkdir -p "$(dirname "$APP/$rel")" && mv "$OLD/$rel" "$APP/$rel"; }} || {{ echo "Could not move $rel"; carried=0; }}
    done < "$STAGE/{CARRY_LIST}"
fi
done_msg="The NLP Suite was updated to $VERSION. Open it again as usual."
if [ "$carried" = 1 ] && [ "$KEEP_BACKUP" = 0 ]; then
    echo "NLP Suite before the update to $VERSION. Deleted the first time the new version starts." > "$OLD/{BACKUP_MARKER}"
else
    echo "Some files of yours are still only in $OLD; it is kept."
    done_msg="$done_msg

Some files of yours are still in the previous version, $OLD (listed in $LOG). Copy what you need, then delete that folder: the next update needs it gone."
fi

xattr -dr com.apple.quarantine "$APP" 2>/dev/null || true
rm -rf "$STAGE"
echo "$(date): done"
tell "$done_msg"
"""


def _ps_quote(text):
    # PowerShell also ends a single-quoted string at the typographic quotes (U+2018/2019/201A/201B);
    # doubling any of them gives that character literally, as with '.
    out = str(text)
    for ch in ("'", "‘", "’", "‚", "‛"):
        out = out.replace(ch, ch + ch)
    return "'" + out + "'"


def windows_swap_script(app, new, backup, stage, version, log, keep_backup=False):  # noqa: PLR0917
    """PowerShell script (Windows) that swaps in the new release once no NLP Suite program is running."""
    q = _ps_quote
    keep = ", ".join(q(k) for k in KEEP_FROM_OLD)
    return f"""# NLP Suite updater, written by NLP_setup_self_update_util.py. Safe to delete.
$App = {q(app)}
$New = {q(new)}
$Old = {q(backup)}
$Stage = {q(stage)}
$Version = {q(version)}
$Log = {q(log)}
$KeepBackup = ${"true" if keep_backup else "false"}
$ProgressPreference = 'SilentlyContinue'
[System.IO.File]::WriteAllText((Join-Path $Stage '{STARTED_FLAG}'), '')
Start-Transcript -LiteralPath $Log -Append | Out-Null
Write-Output "$(Get-Date): updating the NLP Suite in $App to $Version"

function Tell($text) {{
    Write-Output $text
    if ($env:NLP_SUITE_UPDATE_QUIET) {{ return }}  # set by the tests
    try {{
        Add-Type -AssemblyName PresentationFramework
        [System.Windows.MessageBox]::Show($text, 'NLP Suite update') | Out-Null
    }} catch {{ Write-Output "Could not show the message: $_" }}
}}

function Fail($why) {{
    Write-Output "FAILED: $why"
    Remove-Item -LiteralPath $Stage -Recurse -Force -ErrorAction SilentlyContinue
    Tell "The NLP Suite could not be updated to $Version`: $why`n`nYour current version still works. Details are in $Log"
    Stop-Transcript | Out-Null
    exit 1
}}

# Antivirus or File Explorer can hold a folder for a moment after the programs in it exit.
function Move-WithRetry($from, $to) {{
    for ($i = 0; $i -lt 30; $i++) {{
        try {{ Move-Item -LiteralPath $from -Destination $to -ErrorAction Stop; return $true }}
        catch {{ Start-Sleep -Seconds 2 }}
    }}
    return $false
}}

# Wait until no program from the NLP Suite folder is running.
$prefix = $App.TrimEnd('\\') + '\\'
$waited = 0
while (Get-Process | Where-Object {{ $_.Path -and $_.Path.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase) }}) {{
    if ($waited -ge {WAIT_FOR_CLOSE_SECONDS}) {{ Fail 'NLP Suite windows were still open after an hour.' }}
    Start-Sleep -Seconds 2
    $waited += 2
}}

# only a backup this updater marked complete may be deleted; anything else there is the user's
if (Test-Path -LiteralPath $Old) {{
    if (-not (Test-Path -LiteralPath (Join-Path $Old '{BACKUP_MARKER}'))) {{
        Fail "a folder named $Old is in the way and was not deleted. Copy what you need out of it, delete or rename it, and close the NLP Suite again."
    }}
    Remove-Item -LiteralPath $Old -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $Old) {{ Fail "could not remove the old backup $Old." }}
}}
if (-not (Move-WithRetry $App $Old)) {{
    Fail "could not move $App aside. Close any File Explorer window open on that folder and close the NLP Suite again."
}}
if (-not (Move-WithRetry $New $App)) {{
    if (Move-WithRetry $Old $App) {{ Fail 'could not move the new version into place.' }}
    Write-Output 'FAILED: could not move the new version into place, nor the old one back.'
    Tell "The NLP Suite could not be updated to $Version, and its folder could not be put back.`n`nYour NLP Suite is now in $Old. Rename that folder back to $App to use it. Details are in $Log"
    Stop-Transcript | Out-Null
    exit 1
}}

# keep the user's settings
$carried = $true
foreach ($d in @({keep})) {{
    $from = Join-Path $Old $d
    if (Test-Path -LiteralPath $from) {{
        $to = Join-Path $App $d
        try {{
            [System.IO.Directory]::CreateDirectory($to) | Out-Null
            Get-ChildItem -LiteralPath $from -Force | Copy-Item -Destination $to -Recurse -Force -ErrorAction Stop
        }} catch {{ Write-Output "Could not copy ${{d}}: $_"; $carried = $false }}
    }}
}}
# move over the user's own files (listed by user_files: added anywhere, not shipped by the new release)
$carryList = Join-Path $Stage '{CARRY_LIST}'
if (Test-Path -LiteralPath $carryList) {{
    foreach ($rel in [System.IO.File]::ReadAllLines($carryList)) {{
        if (-not $rel) {{ continue }}
        $from = Join-Path $Old $rel
        $to = Join-Path $App $rel
        if (-not (Test-Path -LiteralPath $from)) {{ continue }}
        if (Test-Path -LiteralPath $to) {{ Write-Output "Not moved, the new version has it too: $rel"; $carried = $false; continue }}
        try {{
            [System.IO.Directory]::CreateDirectory((Split-Path -Parent $to)) | Out-Null
            Move-Item -LiteralPath $from -Destination $to -ErrorAction Stop
        }} catch {{ Write-Output "Could not move ${{rel}}: $_"; $carried = $false }}
    }}
}}
$doneMsg = "The NLP Suite was updated to $Version. Open it again as usual."
if ($carried -and -not $KeepBackup) {{
    Set-Content -LiteralPath (Join-Path $Old '{BACKUP_MARKER}') -Value "NLP Suite before the update to $Version. Deleted the first time the new version starts."
}} else {{
    Write-Output "Some files of yours are still only in $Old; it is kept."
    $doneMsg += "`n`nSome files of yours are still in the previous version, $Old (listed in $Log). Copy what you need, then delete that folder: the next update needs it gone."
}}

Remove-Item -LiteralPath $Stage -Recurse -Force -ErrorAction SilentlyContinue
Write-Output "$(Get-Date): done"
Tell $doneMsg
Stop-Transcript | Out-Null
"""


def _delete_backup(backup):
    # the marker goes last, and only once everything else is gone, so a deletion cut short (the NLP Suite
    # closed meanwhile, a locked file, a path too long) is finished the next time the new version starts
    for name in os.listdir(backup):
        if name == BACKUP_MARKER:
            continue
        path = os.path.join(backup, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            try:
                os.remove(path)
            except OSError as e:
                print("Could not delete " + path + ": " + str(e))
    left = [n for n in os.listdir(backup) if n != BACKUP_MARKER]
    if left:
        print("The previous NLP Suite version in " + backup + " is not fully deleted yet; trying again next time.")
        return
    try:
        os.remove(os.path.join(backup, BACKUP_MARKER))
        os.rmdir(backup)
    except OSError as e:
        print("Could not finish deleting the previous NLP Suite version in " + backup + ": " + str(e))


def remove_previous_version(NLPPath, background=True):
    """Delete the version the updater replaced, now that the new one has started.

    Only a backup the swap script marked as complete is deleted. It is a few GB, so by default
    this runs in a background thread and does not delay the menu. Returns the thread, or None.
    """
    backup = update_paths(NLPPath)["backup"]
    if not os.path.isfile(os.path.join(backup, BACKUP_MARKER)):
        return None
    print("Deleting the previous NLP Suite version in " + backup)
    if not background:
        _delete_backup(backup)
        return None
    thread = threading.Thread(target=_delete_backup, args=(backup,), daemon=True)
    thread.start()
    return thread


def write_swap_script(paths, version, sys_platform=None, keep_backup=False):
    """Write the swap script to the temp folder (outside the folders it moves). Returns (script, log)."""
    sys_platform = sys_platform or sys.platform
    temp = tempfile.gettempdir()
    log = os.path.join(temp, "NLP_Suite_update.log")
    new = os.path.join(paths["stage"], APP_FOLDER_IN_ZIP)
    args = (paths["app"], new, paths["backup"], paths["stage"], version, log, keep_backup)
    if sys_platform == "win32":
        script = os.path.join(temp, "NLP_Suite_update.ps1")
        # BOM so Windows PowerShell 5.1 reads non-ASCII folder names correctly
        with open(script, "w", encoding="utf-8-sig") as f:
            f.write(windows_swap_script(*args))
    else:
        script = os.path.join(temp, "NLP_Suite_update.sh")
        with open(script, "w", encoding="utf-8") as f:
            f.write(posix_swap_script(*args))
    return script, log


def launch_swap_script(script, sys_platform=None):
    """Start the swap script detached, so it outlives this process."""
    sys_platform = sys_platform or sys.platform
    cwd = os.path.dirname(script)  # never inside the NLP Suite folder, which Windows would then lock
    devnull = subprocess.DEVNULL
    if sys_platform == "win32":
        flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden"]
        subprocess.Popen(
            [*command, "-File", script],
            cwd=cwd,
            creationflags=flags,
            close_fds=True,
            stdin=devnull,
            stdout=devnull,
            stderr=devnull,
        )
    else:
        subprocess.Popen(
            ["/bin/sh", script], cwd=cwd, start_new_session=True, stdin=devnull, stdout=devnull, stderr=devnull
        )


def swap_script_started(stage, timeout=30.0, poll=0.5):
    """True once the swap script has written its start flag. Group policy or AppLocker can stop
    PowerShell scripts from running at all; without this check the user would wait for nothing."""
    flag = os.path.join(stage, STARTED_FLAG)
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if os.path.exists(flag):
            return True
        time.sleep(poll)
    return os.path.exists(flag)


class _ProgressWindow:
    """A small window with a progress bar and Cancel, shown while the main window is already closed."""

    def __init__(self, title):
        import tkinter as tk
        from tkinter import ttk

        self.cancelled = False
        self._last_redraw = 0.0
        self._phase_start = time.monotonic()
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(False, False)
        self.label = tk.Label(self.root, text="\n ", width=64, anchor="w", justify="left")
        self.label.pack(padx=16, pady=(16, 8))
        self.bar = ttk.Progressbar(self.root, length=440, maximum=100)
        self.bar.pack(padx=16)
        tk.Button(self.root, text="Cancel", command=self._cancel).pack(pady=12)
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)
        self.root.update()

    def _cancel(self):
        self.cancelled = True

    def start_phase(self):
        self._phase_start = time.monotonic()
        self._last_redraw = 0.0

    def show(self, text, done, total):
        fraction = done / total if total else 1.0
        # Redraw at most 10 times a second: the Mac release has over 100,000 files, and redrawing
        # after each one made unpacking take half an hour instead of half a minute.
        now = time.monotonic()
        if now - self._last_redraw < 0.1 and fraction < 1:
            return
        self._last_redraw = now
        left = time_left(done, total, now - self._phase_start)
        self.label.config(text=text + "\n" + (left or " "))
        self.bar["value"] = max(0.0, min(1.0, fraction)) * 100
        self.root.update()

    def close(self):
        self.root.destroy()


def _gb(n):
    return f"{n / 1e9:.1f} GB"


def update_zip_install(NLPPath, GitHub_release_version):
    """Download and stage the new release; a script installs it once the NLP Suite is closed.

    Returns None when the update was handled here (started, declined, cancelled, or reported).
    Otherwise returns why this copy cannot update itself, finishing the sentence "This copy of the
    NLP Suite cannot update itself: ...", and the caller sends the user to the download page.
    """
    import tkinter
    import tkinter.messagebox as mb

    import requests

    version = version_number(GitHub_release_version)
    name = asset_name()
    if name is None:
        return no_download_reason()
    try:
        response = requests.get(RELEASE_API_URL, timeout=15, headers={"Accept": "application/vnd.github+json"})
        response.raise_for_status()
        release = response.json()
    except (requests.RequestException, ValueError) as e:
        print("Could not read the latest NLP Suite release from GitHub: " + str(e))
        return "GitHub could not be reached to download it (" + str(e) + ")."
    found = find_asset(release, name, version)
    if found is None:
        print("The NLP Suite " + version + " download for this computer is not on GitHub yet. Try again later.")
        mb.showinfo(
            title="NLP Suite update",
            message="NLP Suite " + version + " has just been released, but its download is not ready yet (it takes "
            "about an hour to build).\n\nYou will be asked again the next time you close the NLP Suite.",
        )
        return None
    url, size = found

    paths = update_paths(NLPPath)
    parent = os.path.dirname(paths["app"])
    if not os.access(parent, os.W_OK):
        return (
            "it cannot write to the folder that holds it,\n\n"
            + parent
            + "\n\nwhich is where the new version is unpacked. To get automatic updates, move your NLP Suite "
            "folder into a folder you own, such as Documents or Desktop."
        )
    blocker = backup_blocker(paths["backup"])
    if blocker:
        # checked before the download, so 1.5 GB is not fetched for a swap that would stop here
        mb.showwarning(
            title="NLP Suite update",
            message="NLP Suite " + version + " is available, but it cannot be installed yet: " + blocker,
        )
        return None
    # the zip, the unpacked release (about 2.5 times the zip), and room to spare
    needed = size * 4
    free = shutil.disk_usage(parent).free
    if free < needed:
        mb.showwarning(
            title="NLP Suite update",
            message="NLP Suite " + version + " is available, but updating needs about " + _gb(needed) + " of free "
            "disk space and only " + _gb(free) + " is free.\n\nFree up some space and close the NLP Suite again, "
            "or download the new release yourself from\n\n" + RELEASES_URL,
        )
        return None

    onedrive = onedrive_folder(paths["app"])
    onedrive_warning = (
        "\n\nYour NLP Suite folder is inside OneDrive ("
        + onedrive
        + "). OneDrive will upload the whole new version (several GB) and can hold its files while it does, "
        "which may stop the update. Moving the NLP Suite folder out of OneDrive (e.g. to C:\\NLP_Suite) avoids this."
        if onedrive
        else ""
    )
    if not mb.askyesno(
        title="NLP Suite update",
        message="NLP Suite "
        + version
        + " is available.\n\nDownload and install it now? The download is "
        + _gb(size)
        + " and can take several minutes.\n\nYour settings are kept. Your current version is kept in\n\n"
        + paths["backup"]
        + "\n\nuntil the new version starts, and then deleted."
        + onedrive_warning
        + "\n\nIf you say No, you will be asked again the next time you close the NLP Suite.",
    ):
        return None
    try:
        claimed = claim_stage(paths["stage"])
    except OSError as e:
        return "it cannot create the folder it unpacks the new version into (" + str(e) + ")."
    if not claimed:
        print("An NLP Suite update is already in progress.")
        mb.showinfo(
            title="NLP Suite update",
            message="An NLP Suite update is already in progress (started from another window, or within the last "
            "day). If none is, delete the folder\n\n" + paths["stage"] + "\n\nand close the NLP Suite again.",
        )
        return None

    zip_path = os.path.join(paths["stage"], name)
    window = None
    try:
        progress = window = _ProgressWindow("NLP Suite update")
        finished = download(
            url,
            zip_path,
            size,
            on_progress=lambda done, total: progress.show(
                "Downloading NLP Suite " + version + ": " + _gb(done) + " of " + _gb(total), done, total
            ),
            cancelled=lambda: progress.cancelled,
        )
        if finished:
            if shutil.disk_usage(parent).free < unpacked_size(zip_path) + (200 << 20):
                raise OSError("there is not enough free disk space to unpack the new release.")
            progress.start_phase()
            finished = extract_zip(
                zip_path,
                paths["stage"],
                on_progress=lambda done, total: progress.show("Unpacking NLP Suite " + version, done, total),
                cancelled=lambda: progress.cancelled,
            )
        if not finished:
            window.close()
            window = None
            shutil.rmtree(paths["stage"], ignore_errors=True)
            print("NLP Suite update cancelled.")
            return None
        os.remove(zip_path)
        staged_app = os.path.join(paths["stage"], APP_FOLDER_IN_ZIP)
        if not staged_app_ok(staged_app, version):
            raise ValueError("the downloaded release is not NLP Suite " + version + ".")
        progress.show("Finding your own files in the NLP Suite folder, so they are kept", 0, 1)
        carry, changed, complete = user_files(paths["app"], staged_app)
        window.close()
        window = None
        write_carry_list(paths["stage"], carry)
        script, log = write_swap_script(paths, version, keep_backup=not complete)
        with open(log, "a", encoding="utf-8") as f:
            f.write("\nYour files moved to the new version: " + str(len(carry)) + "\n")
            if changed:
                f.write("Release files you changed, kept in " + paths["backup"] + ":\n")
                f.write("".join("    " + rel + "\n" for rel in changed))
            if not complete and not changed:
                f.write(
                    "This copy has no release file list (built before 1.6.41), so " + paths["backup"] + " is kept.\n"
                )
        launch_swap_script(script)
        if not swap_script_started(paths["stage"]):
            raise OSError(
                "the program that installs the new version did not start (this computer may block "
                + ("PowerShell scripts" if sys.platform == "win32" else "shell scripts")
                + ")"
            )
    except (OSError, ValueError, zipfile.BadZipFile, tkinter.TclError, requests.RequestException) as e:
        if window is not None:
            window.close()
        shutil.rmtree(paths["stage"], ignore_errors=True)
        print("NLP Suite update failed: " + str(e))
        mb.showerror(
            title="NLP Suite update",
            message="The NLP Suite could not be updated: "
            + str(e)
            + "\n\nYour current version still works. You can try again the next time you close the NLP Suite, "
            "or download the new release yourself from\n\n" + RELEASES_URL,
        )
        return None

    print("NLP Suite " + version + " is downloaded; it is installed as soon as every NLP Suite window is closed.")
    mb.showinfo(
        title="NLP Suite update",
        message="NLP Suite " + version + " is downloaded. It is installed as soon as every NLP Suite window is closed; "
        "a message tells you when it is done (about a minute).\n\nIf something goes wrong, the details are in\n\n"
        + log,
    )
    return None
