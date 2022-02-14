@echo off
setlocal
ECHO STEP3 will setup a shortcut that by typing NLP in command line/prompt will 1. activate the NLP python environment and 2. change the directory to the NLP/src directory.
ECHO:
ECHO Please wait for the message Installation completed!
echo(
:PROMPT
SET /P AREYOUSURE=Do you wish to continue? [y/n]
IF /I "%AREYOUSURE%" NEQ "y" GOTO END
@echo off
cd %~dp0 && python "..\src\NLP_setup_shortcut_add.py"
:PROMPT
echo(
ECHO Installation completed!
ECHO:
ECHO The NLP shortcut has been added to the environment variables.
ECHO:
ECHO You can double click on NLP_environment_shortcut_remove.bat if you want to remove the shortcut at a later point.
echo(
SET /P ENDPROMPT=Press Return to close this window
EXIT 0
