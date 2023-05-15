@echo off
setlocal
ECHO You are about to remove the NLP shortcut that 1. activates the NLP environment and 2. changes directory to the NLP installation directory by simply typing NLP in command line/prompt.
echo(
SET /P AREYOUSURE=Do you wish to continue? [y/n]
IF /I "%AREYOUSURE%" NEQ "y" GOTO END
@echo off
cd %~dp0 && python "..\src\NLP_setup_shortcut_remove.py"
:PROMPT
echo(
ECHO The NLP shortcut has been removed.
ECHO Double click on STEP3-NLP-environment.bat to add again the NLP shortcut.
SET /P ENDPROMPT=Press Return to close this window.
EXIT 0

:END
:PROMPT
echo(
SET /P ENDPROMPT=Installation Aborted. Press Return to close this window now.
EXIT 0
