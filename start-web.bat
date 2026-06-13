@echo off
REM start-web.bat - double-clickable Windows entrypoint.
REM Forwards to the PowerShell script next to it.

setlocal
set "SCRIPT_DIR=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start-web.ps1" %*
endlocal
