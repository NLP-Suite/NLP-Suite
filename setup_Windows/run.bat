start cmd.exe @cmd /k "conda activate NLP && cd %~dp0/src"
conda activate NLP && cd %~dp0 && Python src/NLP_welcome_main.py && git pull origin