cd "$(dirname "$0")"
cp Mac_run.command ../run.command

source $HOME/anaconda/bin/activate || true

conda create -y -n NLP python=3.9
conda activate NLP

conda install pytorch torchvision cudatoolkit -c pytorch
conda install -y -c conda-forge scikit-learn
pip install -r ../requirements.txt

conda activate NLP
python ../src/download_nltk.py
python ../src/download_jars.py

conda activate NLP
python -m spacy download en
