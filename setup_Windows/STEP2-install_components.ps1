cd %~dp0

conda create -n NLP -y
conda activate NLP

Python -m pip install -r ../requirements.txt

conda activate NLP
Python ../src/download_nltk.py

conda activate NLP
Python -m spacy download en

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\NLP_Suite.lnk")
$Shortcut.TargetPath = "${PSScriptRoot}\run.bat"
$Shortcut.IconLocation = "${PSScriptRoot}\logo.ico"
$Shortcut.Save()

copy run.bat ../run.bat
copy nlp.bat ../nlp.bat

Write-Host "----------------------" -ForegroundColor Green
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "----------------------" -ForegroundColor Green
msg "Installation Complete!"