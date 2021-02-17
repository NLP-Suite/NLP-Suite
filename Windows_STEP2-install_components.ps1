conda create -n NLP -y
conda activate NLP

pip install -r requirements.txt

conda activate NLP
python download_nltk.py

conda activate NLP
python -m spacy download en

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\NLP_Suite.lnk")
$Shortcut.TargetPath = "${PSScriptRoot}\run.bat"
$Shortcut.IconLocation = "${PSScriptRoot}\logo.ico"
$Shortcut.Save()

Write-Host "----------------------" -ForegroundColor Green
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "----------------------" -ForegroundColor Green
msg "Installation Complete!"