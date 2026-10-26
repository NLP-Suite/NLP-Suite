@echo off

echo STEP2 will take a while to install. STEP2 installs Python and all Python and Java packages used by the NLP Suite. Please, be patient and wait for the message Installation Completed!
echo.
echo STEP2 relies on Git. If you have not done so already, please download Git at this link https://git-scm.com/downloads (select the Windows link; it will automatically detect whether your machine is 32-bit or 64-bit on the top line Click here to download the latest...). Run the downloaded exe file.
echo.
set /p AREYOUSURE=Do you wish to continue (Yes if you have already installed Git and wish to continue; No to exit)? [y/n]
if /i not "%AREYOUSURE%"=="y" goto :ContinueScript

cd /d "%~dp0\..\"

call conda create -n NLP python=3.8 -y
call conda activate NLP

call conda install pytorch torchvision cudatoolkit -c pytorch


for /f "delims=" %%k in ('type src\requirements.txt ^| findstr /v "#"') do (
    echo Installing: %%k
    call pip install %%k
)

set ShortcutTarget="%~dp0\run_NLP-Suite.bat"
set ShortcutName="%USERPROFILE%\Desktop\NLP_Suite.lnk"
set ShortcutIcon="%~dp0\logo.ico"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ShortcutName%'); $Shortcut.TargetPath = '%ShortcutTarget%'; $Shortcut.IconLocation = '%ShortcutIcon%'; $Shortcut.Save()"

echo ---------------------- 
echo Installation Completed! Although installation completed, errors may have occurred in the installation of specific Python packages. Please, scroll up to see if errors occurred or use CTRL+F to search for words such as error or fail.
echo ----------------------

:ContinueScript
echo.
echo Press Enter to close this window.
pause >nul
exit /b 0
