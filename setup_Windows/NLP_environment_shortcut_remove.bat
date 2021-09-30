@echo off
setlocal
:PROMPT
SET /P AREYOUSURE=You are removing the NLP shortcut. Do you wish to continue? [y/n]
IF /I "%AREYOUSURE%" NEQ "y" GOTO END

ECHO off
ECHO The shortcut to the current path is now removed. 
ECHO You may now close this window.
cd %~dp0 && python "..\src\remove_shortcut.py"

:END
ECHO Installation Aborted.