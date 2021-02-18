cd "$(dirname "$0")"
xcode-select --install
bash anaconda.sh -b -y -p $HOME/anaconda
source $HOME/anaconda/bin/activate
conda init
conda init zsh