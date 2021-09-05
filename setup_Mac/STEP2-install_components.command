cd "$(dirname "$0")"
cp Mac_run.command ../run.command

source $HOME/anaconda/bin/activate || true
conda activate NLP

if [ $? -ne 0 ]
then
  echo "The script failed with error."
  exit 0
end
conda create -y -n NLP python=3.9

conda install pytorch torchvision cudatoolkit -c pytorch
conda install -y -c conda-forge scikit-learn
pip install -r ../requirements.txt

conda activate NLP
python ../src/download_nltk.py
python ../src/download_jars.py

conda activate NLP
python -m spacy download en
echo "\033[0;31m Errors may have occurred in the installation of specific Python packages. Please, scroll up to see if errors occurred or use CTRL+F to search for words such as “error” or “fail”"
