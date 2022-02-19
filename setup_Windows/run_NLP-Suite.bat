REM Any change in the environment name (NLP) will cause the Run command to fail.
::start cmd.exe @cmd /k "conda activate NLP && cd %~dp0\..\src"
conda activate NLP && cd "%~dp0\..\" && python src/NLP_welcome_main.py && git pull origin current-stable
:PROMPT
echo(
ECHO Installation completed!
echo(
SET /P ENDPROMPT=Press Return to close this window
EXIT 0
