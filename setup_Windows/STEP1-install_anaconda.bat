@echo off
setlocal
ECHO STEP1 will install Anaconda3 on your machine. If these applications are already installed on your machine, the script will exit.
ECHO:
ECHO Please, be patient and wait for the message Installation completed! 
echo(
:PROMPT
SET /P AREYOUSURE=Do you wish to continue? [y/n]
IF /I "%AREYOUSURE%" NEQ "y" GOTO END
curl --ssl-no-revoke -o Anaconda3-Windows-x86_64.exe https://repo.anaconda.com/archive/Anaconda3-2021.05-Windows-x86_64.exe
start /wait "" Anaconda3-Windows-x86_64.exe /InstallationType=JustMe /AddToPath=1 /S /D=%UserProfile%\Anaconda3
:PROMPT
echo(
ECHO Installation completed!
ECHO:
ECHO Anaconda3 and Python have been installed.
echo(
SET /P ENDPROMPT=Press Return to close this window
