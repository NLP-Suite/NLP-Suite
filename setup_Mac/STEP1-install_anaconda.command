cd "$(dirname "$0")"
xcode-select --install
if test -f $HOME/anaconda3/bin/activate; then
    source $HOME/anaconda3/bin/activate
    conda init
    conda init zsh
    exit 0
fi

if test -f $HOME/anaconda/bin/activate; then
    source $HOME/anaconda/bin/activate
    conda init
    conda init zsh
    exit 0
fi

curl -o anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2021.05-MacOSX-x86_64.sh
bash anaconda.sh -b -y -p $HOME/anaconda
source $HOME/anaconda/bin/activate
conda init
conda init zsh