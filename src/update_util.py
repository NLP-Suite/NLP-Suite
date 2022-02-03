"""
Author: David Dai December 22nd, 2021
"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window,"update_util.py",['os','pygit2'])==False:
    sys.exit(0)

import os
from pygit2 import Repository
import tkinter.messagebox as mb

def update_self():
    """
    Update the current script to the latest version.
    """

    if Repository('.').head.shorthand == 'current-stable':
        print("Updating script...")
        os.system("git add -A . ")
        os.system("git stash")
        os.system("git pull -f origin")
        print("Script updated.")
    else:
        mb.showwarning(title='Warning',
                       message="You are not on the current stable branch of the NLP Suite.\n\nYou are on " + Repository('.').head.shorthand + ".\n\nThe automatic update only works from current stable.\n\nUpdate aborted to avoid overwriting your branch.")
