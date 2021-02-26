cd "$(dirname "$0")"
cp Mac_run.command ../run.command

git init ..
git remote add -t \* -f origin https://github.com/NLP-Suite/NLP-Suite.git
git checkout current-stable

source $HOME/anaconda/bin/activate
conda create -y -n NLP python=3.9
conda activate NLP

conda install -y -c conda-forge scikit-learn
conda install pytorch torchvision cudatoolkit -c pytorch
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r ../requirements.txt

conda activate NLP
python ../src/download_nltk.py

conda activate NLP
python -m spacy download en
