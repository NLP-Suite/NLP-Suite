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
    """
    now = time.time() if now is None else now
    if os.path.isdir(stage) and now - os.path.getmtime(stage) > STALE_STAGE_SECONDS:
        shutil.rmtree(stage, ignore_errors=True)
    try:
        os.mkdir(stage)
    except FileExistsError:
        return False
    return True


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


def posix_swap_script(app, new, backup, stage, version, log):
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
exec >>"$LOG" 2>&1
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

rm -rf "$OLD"
[ -e "$OLD" ] && fail "could not remove the old backup $OLD."
mv "$APP" "$OLD" || fail "could not move $APP aside."
if ! mv "$NEW" "$APP"; then
    mv "$OLD" "$APP"
    fail "could not move the new version into place."
fi

# keep the user's settings
carried=1
for d in {keep}; do
    if [ -d "$OLD/$d" ]; then
        {{ mkdir -p "$APP/$d" && cp -Rp "$OLD/$d/." "$APP/$d/"; }} || carried=0
    fi
done
# keep anything the user added to the NLP Suite folder that the release does not ship
for item in "$OLD"/* "$OLD"/.[!.]*; do
    [ -e "$item" ] || continue
    name=$(basename "$item")
    [ -e "$APP/$name" ] || mv "$item" "$APP/$name" || carried=0
done
if [ "$carried" = 1 ]; then
    echo "NLP Suite before the update to $VERSION. Deleted the first time the new version starts." > "$OLD/{BACKUP_MARKER}"
else
    echo "Some files were not carried over; $OLD is kept."
fi

xattr -dr com.apple.quarantine "$APP" 2>/dev/null || true
rm -rf "$STAGE"
echo "$(date): done"
tell "The NLP Suite was updated to $VERSION. Open it again as usual."
"""


def _ps_quote(text):
    return "'" + str(text).replace("'", "''") + "'"


def windows_swap_script(app, new, backup, stage, version, log):
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
$ProgressPreference = 'SilentlyContinue'
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

if (Test-Path -LiteralPath $Old) {{
    Remove-Item -LiteralPath $Old -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $Old) {{ Fail "could not remove the old backup $Old." }}
}}
if (-not (Move-WithRetry $App $Old)) {{
    Fail "could not move $App aside. Close any File Explorer window open on that folder and close the NLP Suite again."
}}
if (-not (Move-WithRetry $New $App)) {{
    Move-WithRetry $Old $App | Out-Null
    Fail 'could not move the new version into place.'
}}

# keep the user's settings
$carried = $true
foreach ($d in @({keep})) {{
    $from = Join-Path $Old $d
    if (Test-Path -LiteralPath $from) {{
        $to = Join-Path $App $d
        try {{
            New-Item -ItemType Directory -Force -Path $to -ErrorAction Stop | Out-Null
            Get-ChildItem -LiteralPath $from -Force | Copy-Item -Destination $to -Recurse -Force -ErrorAction Stop
        }} catch {{ Write-Output "Could not copy ${{d}}: $_"; $carried = $false }}
    }}
}}
# keep anything the user added to the NLP Suite folder that the release does not ship
Get-ChildItem -LiteralPath $Old -Force | ForEach-Object {{
    $dest = Join-Path $App $_.Name
    if (-not (Test-Path -LiteralPath $dest)) {{
        try {{ Move-Item -LiteralPath $_.FullName -Destination $dest -ErrorAction Stop }}
        catch {{ Write-Output "Could not move $($_.Exception.Message)"; $carried = $false }}
    }}
}}
if ($carried) {{
    Set-Content -LiteralPath (Join-Path $Old '{BACKUP_MARKER}') -Value "NLP Suite before the update to $Version. Deleted the first time the new version starts."
}} else {{
    Write-Output "Some files were not carried over; $Old is kept."
}}

Remove-Item -LiteralPath $Stage -Recurse -Force -ErrorAction SilentlyContinue
Write-Output "$(Get-Date): done"
Tell "The NLP Suite was updated to $Version. Open it again as usual."
Stop-Transcript | Out-Null
"""


def _delete_backup(backup):
    # the marker goes last, so a deletion cut short (the NLP Suite closed meanwhile) is finished next time
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


def write_swap_script(paths, version, sys_platform=None):
    """Write the swap script to the temp folder (outside the folders it moves). Returns (script, log)."""
    sys_platform = sys_platform or sys.platform
    temp = tempfile.gettempdir()
    log = os.path.join(temp, "NLP_Suite_update.log")
    new = os.path.join(paths["stage"], APP_FOLDER_IN_ZIP)
    args = (paths["app"], new, paths["backup"], paths["stage"], version, log)
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


class _ProgressWindow:
    """A small window with a progress bar and Cancel, shown while the main window is already closed."""

    def __init__(self, title):
        import tkinter as tk
        from tkinter import ttk

        self.cancelled = False
        self._last_redraw = 0.0
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(False, False)
        self.label = tk.Label(self.root, text="", width=64, anchor="w", justify="left")
        self.label.pack(padx=16, pady=(16, 8))
        self.bar = ttk.Progressbar(self.root, length=440, maximum=100)
        self.bar.pack(padx=16)
        tk.Button(self.root, text="Cancel", command=self._cancel).pack(pady=12)
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)
        self.root.update()

    def _cancel(self):
        self.cancelled = True

    def show(self, text, fraction):
        # Redraw at most 10 times a second: the Mac release has over 100,000 files, and redrawing
        # after each one made unpacking take half an hour instead of half a minute.
        now = time.monotonic()
        if now - self._last_redraw < 0.1 and fraction < 1:
            return
        self._last_redraw = now
        self.label.config(text=text)
        self.bar["value"] = max(0.0, min(1.0, fraction)) * 100
        self.root.update()

    def close(self):
        self.root.destroy()


def _gb(n):
    return f"{n / 1e9:.1f} GB"


def update_zip_install(NLPPath, GitHub_release_version):
    """Download and stage the new release; a script installs it once the NLP Suite is closed.

    Returns True when the update was handled here (started, declined, cancelled, or reported),
    False when the caller should fall back to sending the user to the download page.
    """
    import tkinter
    import tkinter.messagebox as mb

    import requests

    version = version_number(GitHub_release_version)
    name = asset_name()
    if name is None:
        return False
    try:
        response = requests.get(RELEASE_API_URL, timeout=15, headers={"Accept": "application/vnd.github+json"})
        response.raise_for_status()
        release = response.json()
    except (requests.RequestException, ValueError) as e:
        print("Could not read the latest NLP Suite release from GitHub: " + str(e))
        return False
    found = find_asset(release, name, version)
    if found is None:
        print("The NLP Suite " + version + " download for this computer is not on GitHub yet. Try again later.")
        return True
    url, size = found

    paths = update_paths(NLPPath)
    parent = os.path.dirname(paths["app"])
    if not os.access(parent, os.W_OK):
        return False
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
        return True

    if not mb.askyesno(
        title="NLP Suite update",
        message="NLP Suite "
        + version
        + " is available.\n\nDownload and install it now? The download is "
        + _gb(size)
        + " and can take several minutes.\n\nYour settings are kept. Your current version is kept in\n\n"
        + paths["backup"]
        + "\n\nuntil the new version starts, and then deleted.\n\nIf you say No, you will be asked again the next time you close the NLP Suite.",
    ):
        return True
    if not claim_stage(paths["stage"]):
        print("An NLP Suite update is already in progress.")
        return True

    zip_path = os.path.join(paths["stage"], name)
    window = None
    try:
        progress = window = _ProgressWindow("NLP Suite update")
        finished = download(
            url,
            zip_path,
            size,
            on_progress=lambda done, total: progress.show(
                "Downloading NLP Suite " + version + ": " + _gb(done) + " of " + _gb(total), done / total
            ),
            cancelled=lambda: progress.cancelled,
        )
        if finished:
            if shutil.disk_usage(parent).free < unpacked_size(zip_path) + (200 << 20):
                raise OSError("there is not enough free disk space to unpack the new release.")
            finished = extract_zip(
                zip_path,
                paths["stage"],
                on_progress=lambda done, total: progress.show("Unpacking NLP Suite " + version, done / total),
                cancelled=lambda: progress.cancelled,
            )
        window.close()
        window = None
        if not finished:
            shutil.rmtree(paths["stage"], ignore_errors=True)
            print("NLP Suite update cancelled.")
            return True
        os.remove(zip_path)
        if not staged_app_ok(os.path.join(paths["stage"], APP_FOLDER_IN_ZIP), version):
            raise ValueError("the downloaded release is not NLP Suite " + version + ".")
        script, log = write_swap_script(paths, version)
        launch_swap_script(script)
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
        return True

    print("NLP Suite " + version + " is downloaded; it is installed as soon as every NLP Suite window is closed.")
    mb.showinfo(
        title="NLP Suite update",
        message="NLP Suite " + version + " is downloaded. It is installed as soon as every NLP Suite window is closed; "
        "a message tells you when it is done (about a minute).\n\nIf something goes wrong, the details are in\n\n"
        + log,
    )
    return True
