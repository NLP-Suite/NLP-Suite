cd "$(dirname "$0")"
xcode-select --install
curl -o anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2021.05-MacOSX-x86_64.sh
bash anaconda.sh -b -y -p $HOME/anaconda
source $HOME/anaconda/bin/activate
conda init
conda init zsh