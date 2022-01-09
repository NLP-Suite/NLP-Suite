cd "${PSScriptRoot}\..\"

conda create -n NLP -y
conda activate NLP

conda install pytorch torchvision cudatoolkit -c pytorch
python -m pip install -r requirements.txt

conda activate NLP
python src\download_nltk_stanza.py
python src\download_jars.py

conda activate NLP
python -m spacy download en

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\NLP_Suite.lnk")
$Shortcut.TargetPath = "${PSScriptRoot}\run_NLP-Suite.bat"
$Shortcut.IconLocation = "${PSScriptRoot}\logo.ico"
$Shortcut.Save()

Write-Host "----------------------" -ForegroundColor Green
Write-Host "Installation Completed! Although installation completed, errors may have occurred in the installation of specific Python packages. Please, scroll up to see if errors occurred or use CTRL+F to search for words such as error or fail." -ForegroundColor Green
Write-Host "----------------------" -ForegroundColor Green
