echo "STEP2 relies on Git. If you have not done so already, please download Git at this link https://git-scm.com/downloads (select the macOS link and then download and install Xcode (if space allows; if you have limited disk space, use the binary installer)."
echo
while true; do
    read -p "Do you wish to continue (Yes if you have already installed Git and wish to continue; No to exit)? [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "STEP2 Aborted." && exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

cd "$(dirname "$0")"

git init ..
git remote add -t \* -f origin https://github.com/NLP-Suite/NLP-Suite.git
git checkout -f current-stable
git add -A .
git stash
git pull -f origin current-stable

if test -f $HOME/anaconda3/bin/activate; then
    source $HOME/anaconda3/bin/activate
fi

if test -f $HOME/anaconda/bin/activate; then
    source $HOME/anaconda/bin/activate
fi

conda create -y -n NLP python=3.9
conda activate NLP

conda install pytorch torchvision cudatoolkit -c pytorch
pip install -r ../requirements.txt

conda activate NLP
python ../src/download_nltk_stanza.py
python ../src/download_jars.py

conda activate NLP
python -m spacy download en

echo "\033[0;31m Errors may have occurred in the installation of specific Python packages. Please, scroll up to see if errors occurred or use CTRL+F to search for words such as error or fail"
