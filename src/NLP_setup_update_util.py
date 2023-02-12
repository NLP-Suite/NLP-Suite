"""
Author: David Dai December 22nd, 2021
Edited Roberto Franzosi February/September 2022
"""

import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "NLP_setup_update_util.py",
                                          ['pygit2']) == False:
    sys.exit(0)

import atexit  # a Python module
# from NLP_setup_update_util import update_self
from pygit2 import Repository
import sys
import os
import stat
import tkinter.messagebox as mb
import shutil
import subprocess

import IO_user_interface_util
import config_util

#config_filename has no path;
# config_input_output_numeric_options is set to [0 0,0,0] for GUIs that are placeholders for more specialized GUIs
#   in these cases (e.g., narrative_analysis_ALL_main, there are no I/O options to save
# current_config_input_output_alphabetic_options value returned in GUI_util by config_util.read_config_file
# called from GUI_util when hitting CLOSE
def exit_window(window, local_release_version, GitHub_release_version):
    # if IO_libraries_util.install_all_Python_packages(window, "GUI_IO_util.py",
    #                                           ['pygit2']) == False:
    #     sys.exit(0)

    # config_input_output_numeric_options is a list such as [6, 1, 0, 1]
    # current_config_input_output_alphabetic_options a list such as
    #   ['C:/Users/rfranzo/Desktop/NLP-Suite/lib/sampleData/newspaperArticles/A Spool of Blue Thread_Anne Tyler_Rebecca Pepper Sinkler_02-13-2015.txt', '', '', 'C:/Program Files (x86)/NLP_backup/Output']
    def exit_handler():
        os.environ["NLP_SUITE_OPEN_WINDOWS"] = str(int(os.environ["NLP_SUITE_OPEN_WINDOWS"]) - 1)
        # if there are still other windows open, don't download new code
        if int(os.environ["NLP_SUITE_OPEN_WINDOWS"]) != 0:
            return

        try:
            # set equal to test
            # local_release_version = GitHub_release_version
            if GitHub_release_version != local_release_version:
                errorFound = update_self(window, GitHub_release_version)
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
                    '\nYour NLP Suite is up-to-date with the latest release available on GitHub (' + GitHub_release_version + ').')
        except Exception as e:
            print(str(e))
    # when closing NLP Suite via terminal
    atexit.register(exit_handler)

    window.destroy()
    sys.exit(0)

# called by exit_window
# returns True when error found
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
            return True
    try:
        if Repository('.').head.shorthand == 'current-stable':
            print("Updating the NLP Suite...")
            os.system("git add -A . ")
            os.system("git stash")
            os.system("git pull -f origin")
            print(message_update)
            mb.showwarning(title='Warning',
                           message=message_update)
            return True
        else:
            print("\nYou are not working on the 'current-stable' branch of the NLP Suite. You are on the '" + Repository('.').head.shorthand + "' branch. Update aborted to avoid overwriting your branch.")
            return True
    except Exception as e:
        print('Git fatal error:' + str(e))
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
                    print("The .git folder STILL exists after remove. The delete .git folder did not work.\n\nPlease, delete manually the .git folder and try again.\n\nUpdate aborted.")
                    return True
            except Exception as e:
                if 'PermissionError' in str(e):
                    message = "The algorithm encountered a permission error in deleting the .git subfolder of your main NLP Suite folder (" + NLPPath + ").\n\nPlease, make sure that you do not have the ,git folder open and try again.\n\nYou may also delete manually the .git folder and try again.\n\nUpdate aborted."
                    print(message)
                    mb.showwarning(title='.git folder permission error',
                                   message=message)

        IO_user_interface_util.timed_alert('', 3000, '.git reinitialization and files update',
                                           'Started running NLP Suite auto-update at', True, 'Please be patient...')

        try:
            # reinitializes git & pulls current-stable
            os.system("git init .. ")
            # os.system("git remote add -t \* -f origin https://github.com/NLP-Suite/NLP-Suite.git")
            # os.system("git remote add -f origin https://github.com/NLP-Suite/NLP-Suite.git")
            os.system("git remote add -m current-stable -f origin https://github.com/NLP-Suite/NLP-Suite.git")
            os.system("git checkout -f current-stable")
            os.system("git add -A .")
            os.system("git stash")
            os.system("git pull -f origin current-stable")
        except:
            return True
