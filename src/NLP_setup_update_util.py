"""
Author: David Dai December 22nd, 2021
Edited Roberto Franzosi February 2022
"""

import sys
import requests
import webbrowser
import tkinter as tk
import subprocess

import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"NLP_setup_update_util.py",['os','pygit2'])==False:
    sys.exit(0)

import os
import stat
from pygit2 import Repository
import tkinter.messagebox as mb
import shutil

def update_self(window,GitHub_release_version):
    """
    Update the current script to the latest version.
    """

    if sys.platform == 'win32':  # Windows
        url = 'https://git-scm.com/download/win'
        Git_download = url + '\n\nThe Git website will automatically detect whether your machine is 32-bit or 64-bit on the top line Click here to download the latest...'
    else:
        url = 'https://git-scm.com/download/mac'
        Git_download = url + '\n\nInstall Xcode if you do not have disk space problems; otherwise download the Binary installer.'

    message_Git = 'The NLP Suite update function relies on Git.\n\nGit is not installed on your machine.\n\nGit can be downloaded at this link ' + Git_download + '\n\nAfter downloading Git, run the downloaded exe file. You need to do this only once.\n\nDo you want to open the Git website now and install it?'
    message_update = "The NLP Suite was successfully updated to the latest release available on GitHub: " + str(
        GitHub_release_version) + "\n\nThe next time you fire up the NLP Suite it will use this release."


    # testing for Git
    # https: // stackoverflow.com / questions / 11113896 / use - git - commands - within - python - code
    try:
        subprocess.call(["git", "pull"])
    except:
        if not IO_libraries_util.open_url('Git', url, ask_to_open=True, message_title='Git installation', message=message_Git):
            return
    try:
        if Repository('.').head.shorthand == 'current-stable':
            print("Updating the NLP Suite...")
            os.system("git add -A . ")
            os.system("git stash")
            os.system("git pull -f origin")
            mb.showwarning(title='Warning',
                           message=message_update)
            print(message_update)
        else:
            print("\nYou are not working on the 'current-stable' branch of the NLP Suite. You are on the '" + Repository('.').head.shorthand + "' branch. Update aborted to avoid overwriting your branch.")
    except Exception as e:
        print('Git fatal error:' + str(e))
        # mb.warning(e);  # or print(e)
        mb.showwarning(title='Git fatal error',
                   message="Git encountered an error in executing the command 'Repository('.').head.shorthand.\n\nError: " + str(e) + "\n\nUpdate aborted.")

        # removes git
        NLPPath = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + os.sep + os.pardir)
        git_folder = NLPPath + os.sep + '.git'
        # check that .git folder exists
        if os.path.exists(git_folder):
            # .git is readonly need to change to avoid permission error
            os.chmod(git_folder, stat.S_IRWXU) # O Others U Owner
            try:
                shutil.rmtree(git_folder)
                if os.path.exists(git_folder):
                    print("The folder STILL exists after remove. The delete .git directory did not work.")
                    return
            except Exception as e:
                if 'PermissionError' in str(e):
                    message = "The algorithm encountered a permission error in deleting the .git subfolder of your main NLP Suite folder (" + NLPPath + ").\n\nPlease, make sure that you do not have the ,git subfolder open and try again.\n\nUpdate aborted."
                    print(message)
                    mb.showwarning(title='.git subfolder permission error',
                                   message=message)

        # reinitializes git & pulls current-stable
        os.system("git init .. ")
        # os.system("git remote add -t \* -f origin https://github.com/NLP-Suite/NLP-Suite.git")
        # os.system("git remote add -f origin https://github.com/NLP-Suite/NLP-Suite.git")
        os.system("git remote add -m current-stable -f origin https://github.com/NLP-Suite/NLP-Suite.git")
        os.system("git checkout -f current-stable")
        os.system("git add -A .")
        os.system("git stash")
        os.system("git pull -f origin current-stable")
