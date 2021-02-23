cd "$(dirname "$0")"

git init ..
git remote add -t \* -f origin https://github.com/NLP-Suite/NLP-Suite.git
git checkout current

source $HOME/anaconda/bin/activate
conda create -y -n NLP python=3.9
conda activate NLP

cp run.command ../run.command

conda install -y -c conda-forge scikit-learn
pip install -r ../requirements.txt

conda activate NLP
Python ../src/download_nltk.py

conda activate NLP
Python -m spacy download en
