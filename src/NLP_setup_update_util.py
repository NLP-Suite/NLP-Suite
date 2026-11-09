"""
Author: David Dai December 22nd, 2021
Edited Roberto Franzosi February/September 2022
"""

# This module reports update progress to the terminal on exit, after the GUI window is gone.
# ruff: noqa: T201

import atexit  # a Python module
import os
import shutil
import stat
import subprocess
import sys
import tkinter.messagebox as mb

import GUI_IO_util
import GUI_util
import IO_libraries_util
import IO_user_interface_util

window = GUI_util.window

# config_filename has no path;
# config_input_output_numeric_options is set to [0 0,0,0] for GUIs that are placeholders for more specialized GUIs
#   in these cases (e.g., narrative_analysis_ALL_main, there are no I/O options to save
# current_config_input_output_alphabetic_options value returned in GUI_util by config_util.read_config_file


# called from GUI_util, NLP_welcome_main, and the 3 NLP_setup scripts since they handle their own CLOSE
def exit_window():
    global local_release_version, GitHub_release_version  # so that it can be used in the sub-function exit_handler()
    local_release_version = GUI_util.get_local_release_version()
    GitHub_release_version = GUI_util.get_GitHub_release_version()

    # if IO_libraries_util.install_all_Python_packages(window, "GUI_IO_util.py",
    #                                           ['pygit2']) == False:
    #     sys.exit(0)

    # config_input_output_numeric_options is a list such as [6, 1, 0, 1]
    # current_config_input_output_alphabetic_options a list such as
    #   ['C:/Users/rfranzo/Desktop/NLP-Suite/lib/sampleData/newspaperArticles/A Spool of Blue Thread_Anne Tyler_Rebecca Pepper Sinkler_02-13-2015.txt', '', '', 'C:/Program Files (x86)/NLP_backup/Output']
    def exit_handler():
        os.environ["NLP_SUITE_OPEN_WINDOWS"] = str(int(os.environ["NLP_SUITE_OPEN_WINDOWS"]) - 1)
        # if there are still other windows open, don't display the message of downloading a new release and do not download
        if int(os.environ["NLP_SUITE_OPEN_WINDOWS"]) != 0:
            return

        try:
            # set equal to test
            # local_release_version = GitHub_release_version
            if newer_release_available(local_release_version, GitHub_release_version):
                # GitHub_release_version, local_release_version contain \n that must be removed for display
                # the question is annoying for most users that are not developers
                # answer = tk.messagebox.askyesno("Warning", "Your local NLP Suite version " + str(local_release_version[:-1]) + " is not up-to-date with the release currently available on GitHub " + str(GitHub_release_version[:-1]) + ".\n\nDo you want to update your local version, pulling from GitHub?\n\nIF YOU ARE AN NLP SUITE DEVELOPER, PULLING FROM GitHub WILL OVERWRITE ANY CODE YOU WILL HAVE WRITTEN.")
                # if not answer:
                #     return
                update_self(GitHub_release_version)
            else:
                # should test for stack and not print if 'NLP_menu_main' or 'NLP_welcome_main' are open
                # import psutil
                # proc = psutil.Process()
                # print(proc.open_files())
                # import inspect
                # inspect.stack() will return the stack information
                # ScriptName = inspect.stack()
                # if not "NLP_setup_IO_main.py" in ScriptName:
                #     print("ScriptName", ScriptName)
                print(
                    "\nYour NLP Suite is up-to-date with the latest release available on GitHub ("
                    + GitHub_release_version
                    + ")."
                )
        except Exception as e:
            print(str(e))

    # when closing NLP Suite via terminal
    atexit.register(exit_handler)

    window.destroy()
    sys.exit(0)


RELEASES_URL = "https://github.com/NLP-Suite/NLP-Suite/releases/latest"


def _release_tuple(version):
    parts = str(version).strip().lstrip("vV").split(".")
    if not parts or not all(p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in (parts + ["0", "0", "0"])[:3])


def newer_release_available(local_version, GitHub_version):
    """True only when GitHub's release is a real version newer than the local one.

    GitHub_version is "0.0.0" when the computer is offline; that, an unreadable version, or a local
    version ahead of GitHub (a developer copy) must not start an update.
    """
    local, remote = _release_tuple(local_version), _release_tuple(GitHub_version)
    return local is not None and remote is not None and remote > local


def update_method(NLPPath, frozen=None):
    """How this install can be updated.

    "download": the installer build, or any folder that is not a git checkout. git pull cannot
        work here, so the user is sent to the latest release on GitHub.
    "install_git": a git checkout, but the git program is missing.
    "git": a git checkout with git available.
    """
    if frozen is None:
        frozen = getattr(sys, "frozen", False)
    if frozen or not os.path.isdir(os.path.join(NLPPath, ".git")):
        return "download"
    if shutil.which("git") is None:
        return "install_git"
    return "git"


def read_git_branch(NLPPath):
    """(branch, error): the checked-out branch, or None and git's error text. Uses the git program, not pygit2."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=NLPPath,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return None, "Could not run git: " + str(e)
    if result.returncode != 0:
        return None, (result.stderr or "").strip() or "git rev-parse exited with code " + str(result.returncode)
    return (result.stdout.strip() or None), ""


def current_git_branch(NLPPath):
    """Name of the checked-out branch, or None if git cannot read it."""
    return read_git_branch(NLPPath)[0]


# Only these errors mean the .git folder itself is broken and may be rebuilt from GitHub. Anything else
# (e.g. "detected dubious ownership" when the folder belongs to another Windows account, a git lock, a
# timeout) leaves .git alone: deleting it would destroy a working checkout and the user's branches.
_DAMAGED_GIT_ERRORS = ("not a git repository", "corrupt", "bad object", "loose object", "bad index file")


def git_folder_is_damaged(error):
    text = str(error or "").lower()
    return "dubious ownership" not in text and any(e in text for e in _DAMAGED_GIT_ERRORS)


# called by exit_window
# returns True when error found
def update_self(GitHub_release_version):
    """
    Update the current script to the latest version.
    """

    NLPPath = GUI_IO_util.NLPPath
    method = update_method(NLPPath)

    if method == "download":
        message_download = (
            "A new release of the NLP Suite is available on GitHub: "
            + str(GitHub_release_version).strip()
            + ".\n\nThis copy of the NLP Suite cannot update itself. Download the new release from\n\n"
            + RELEASES_URL
            + "\n\nunzip it, and replace your current NLP_Suite folder.\n\nDo you want to open the download page now?"
        )
        IO_libraries_util.open_url(
            "NLP Suite release",
            RELEASES_URL,
            ask_to_open=True,
            message_title="NLP Suite update",
            message=message_download,
        )
        return True

    if sys.platform == "win32":  # Windows
        url = "https://git-scm.com/download/win"
        Git_download = (
            url
            + "\n\nThe Git website will automatically detect whether your machine is 32-bit or 64-bit on the top line Click here to download the latest..."
        )
    else:
        url = "https://git-scm.com/download/mac"
        Git_download = (
            url + "\n\nInstall Xcode if you do not have disk space problems; otherwise download the Binary installer."
        )

    message_Git = (
        "The NLP Suite update function relies on Git.\n\nGit is not installed on your machine.\n\nGit can be downloaded at this link "
        + Git_download
        + "\n\nAfter downloading Git, run the downloaded exe file. You need to do this only once.\n\nDo you want to open the Git website now and install it?"
    )
    message_update = (
        "The NLP Suite was successfully updated to the latest release available on GitHub: "
        + str(GitHub_release_version)
        + "\n\nThe next time you fire up the NLP Suite it will use this release."
    )

    if method == "install_git":
        IO_libraries_util.open_url("Git", url, ask_to_open=True, message_title="Git installation", message=message_Git)
        return True

    branch, git_error = read_git_branch(NLPPath)
    if branch == "current-stable":
        print("Updating the NLP Suite...")
        for command in (["git", "add", "-A", "."], ["git", "stash"], ["git", "pull", "-f", "origin"]):
            subprocess.run(command, cwd=NLPPath)
        print(message_update)
        mb.showwarning(title="Warning", message=message_update)
        return True
    if branch is not None:
        print(
            "\nYou are not working on the 'current-stable' branch of the NLP Suite. You are on the '"
            + branch
            + "' branch. Update aborted to avoid overwriting your branch."
        )
        return True

    if not git_folder_is_damaged(git_error):
        print("Git error: " + git_error + "\nUpdate aborted; the .git folder was left as it is.")
        mb.showwarning(
            title="NLP Suite update",
            message="The NLP Suite could not be updated, because Git reported this error in your NLP Suite folder ("
            + NLPPath
            + "):\n\n"
            + git_error
            + "\n\nNothing was changed. You can update by hand with 'git pull' in that folder, or download the new "
            "release from\n\n" + RELEASES_URL,
        )
        return True

    # git says the .git folder itself is damaged. Rebuild it from GitHub.
    print("Git fatal error: could not read the current branch with 'git rev-parse'.")
    mb.showwarning(
        title="Git fatal error",
        message="Git could not read the current branch of your NLP Suite folder ("
        + NLPPath
        + ").\n\nThe .git folder will be rebuilt from GitHub.",
    )

    # removes git
    git_folder = NLPPath + os.sep + ".git"
    # check that .git folder exists
    if os.path.exists(git_folder):
        # .git is readonly need to change to avoid permission error
        os.chmod(git_folder, stat.S_IRWXU)  # O Others U Owner
        try:
            shutil.rmtree(git_folder)
            if os.path.exists(git_folder):
                print(
                    "The .git folder STILL exists after remove. The delete .git folder did not work.\n\nPlease, delete manually the .git folder and try again.\n\nUpdate aborted."
                )
                return True
        except Exception as e:
            if "PermissionError" in str(e):
                message = (
                    "The algorithm encountered a permission error in deleting the .git subfolder of your main NLP Suite folder ("
                    + NLPPath
                    + ").\n\nPlease, make sure that you do not have the ,git folder open and try again.\n\nYou may also delete manually the .git folder and try again.\n\nUpdate aborted."
                )
                print(message)
                mb.showwarning(title=".git folder permission error", message=message)

    IO_user_interface_util.timed_alert(
        "",
        3000,
        ".git reinitialization and files update",
        "Started running NLP Suite auto-update at",
        True,
        "Please be patient...",
    )

    # reinitializes git in the NLP Suite folder & pulls current-stable
    commands = (
        ["git", "init", "."],
        ["git", "remote", "add", "-m", "current-stable", "-f", "origin", "https://github.com/NLP-Suite/NLP-Suite.git"],
        ["git", "checkout", "-f", "current-stable"],
        ["git", "add", "-A", "."],
        ["git", "stash"],
        ["git", "pull", "-f", "origin", "current-stable"],
    )
    try:
        for command in commands:
            subprocess.run(command, cwd=NLPPath)
    except (OSError, subprocess.SubprocessError) as e:
        mb.showwarning(title="Git fatal error", message="Rebuilding the .git folder failed.\n\nError: " + str(e))
        return True
