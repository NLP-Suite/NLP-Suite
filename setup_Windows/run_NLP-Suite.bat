@echo off
setlocal
REM Any change in the environment name (NLP) will cause the Run command to fail.
call conda activate NLP
cd "%~dp0\..\"
call python src/NLP_welcome_main.py
echo Press any key to exit
:PROMPT
echo(
echo(
SET /P ENDPROMPT=Press Return to close this window