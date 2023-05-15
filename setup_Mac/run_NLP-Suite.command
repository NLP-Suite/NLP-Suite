if test -f $HOME/anaconda3/bin/activate; then
    source $HOME/anaconda3/bin/activate
fi

if test -f $HOME/anaconda/bin/activate; then
    source $HOME/anaconda/bin/activate
fi

if test -f $HOME/opt/anaconda3/bin/activate; then
    source $HOME/opt/anaconda3/bin/activate
fi

conda activate NLP
cd "$(dirname "$0")"
python ../src/NLP_welcome_main.py
git pull -f origin current-stable