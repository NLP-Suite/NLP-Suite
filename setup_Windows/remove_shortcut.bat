ECHO off
ECHO The shortcut to the current path is now removed. 
ECHO You may now close this window.
cd %~dp0 && python3 ../src/remove_shortcut.py