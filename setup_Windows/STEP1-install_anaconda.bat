curl --ssl-no-revoke -o Anaconda3-Windows-x86_64.exe https://repo.anaconda.com/archive/Anaconda3-2021.05-Windows-x86_64.exe
start /wait "" Anaconda3-Windows-x86_64.exe /InstallationType=JustMe /AddToPath=1 /S /D=%UserProfile%\Anaconda3
:PROMPT
echo(
ECHO The Anaconda3 installation is complete.
echo(
SET /P ENDPROMPT=Press Return to close this window.
EXIT 0