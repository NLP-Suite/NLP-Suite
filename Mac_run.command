source $HOME/anaconda/bin/activate
conda activate NLP
cd "$(dirname "$0")"
python src/NLP_welcome_main.py
git pull origin