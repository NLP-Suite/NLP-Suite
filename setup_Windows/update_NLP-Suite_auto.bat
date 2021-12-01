@echo off
setlocal
ECHO You are about to setup automatic update of the NLP Suite every time you close the NLP Suite, pulling the newest release from GitHub.
ECHO The advantage is that you will have to run this command only once.
ECHO For this to happen, though, you will need to be connected to the internet.
ECHO You will also need the freeware Git installed on your machine. Download Git at https://git-scm.com/downloads, if it has not been installed already.
ECHO The update_NLP-Suite_auto.bat ONLY WORKS IF YOU OPEN THE NLP SUITE FROM THE DESKTOP ICON OR THE run_NLP-Suite.bat. IT DOES NOT WORK IF YOU RUN IN COMMAND/PROMPT python NLP_welcome_main.py or python NLP_menu_main.py 
echo(
SET /P AREYOUSURE=Do you wish to continue? [y/n]
IF /I "%AREYOUSURE%" NEQ "y" GOTO END
@echo off

cd "%~dp0..\" && git init . && git remote add -t * -f origin https://github.com/NLP-Suite/NLP-Suite.git && git checkout -f current-stable && git add -A . && git stash
IF /I "%AREYOUSURE%" NEQ "y" GOTO END
@echo off

:PROMPT
echo(
ECHO You are set. The NLP Suite will automatically update every time you close the NLP Suite, pulling the newest release from GitHub.
ECHO REMEMBER! The update_NLP-Suite_auto.bat ONLY WORKS IF YOU OPEN THE NLP SUITE FROM THE DESKTOP ICON OR THE run_NLP-Suite.bat. IT DOES NOT WORK IF YOU RUN IN COMMAND/PROMPT python NLP_welcome_main.py or python NLP_menu_main.py 

echo(
SET /P ENDPROMPT=Press Return to close this window.
EXIT 0

:END
:PROMPT
echo(
SET /P ENDPROMPT=Installation Aborted. Press Return to close this window now.
EXIT 0
