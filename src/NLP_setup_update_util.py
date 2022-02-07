"""
Author: David Dai December 22nd, 2021
Edited Roberto Franzosi February 2022
"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"NLP_setup_update_util.py",['os','pygit2'])==False:
    sys.exit(0)

import os
from pygit2 import Repository
import tkinter.messagebox as mb

def update_self(window,GitHub_release_version):
    """
    Update the current script to the latest version.
    """

    message = "The NLP Suite was successfully updated to the latest release available on GitHub: " + str(
        GitHub_release_version) + "\n\nThe next time you fire up the NLP Suite it will use this release."

    if Repository('.').head.shorthand == 'current-stable':
        print("Updating the NLP Suite...")
        os.system("git add -A . ")
        os.system("git stash")
        os.system("git pull -f origin")
        mb.showwarning(title='Warning',
                       message=message)
        print(message)
    else:
        print("You are not working on the 'current-stable' branch of the NLP Suite. You are on the '" + Repository('.').head.shorthand + "' branch'. Update aborted to avoid overwriting your branch.")
        # mb.showwarning(title='Warning',
        #                message="You are not on the current stable branch of the NLP Suite.\n\nYou are on " + Repository('.').head.shorthand + ".\n\nThe automatic update only works from current stable.\n\nUpdate aborted to avoid overwriting your branch.")
