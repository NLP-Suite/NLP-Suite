echo "STEP1 will install Anaconda3 and Python on your machine. If these applications are already installed on your machine, the script will exit."
echo
echo "Please, be patient and wait for the message Installation completed!"
echo
while true; do
    read -p "Do you wish to continue? [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Setup Aborted." && exit;;
        * ) echo "Please answer yes or no.";;
    esac
donecd "$(dirname "$0")"
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
echo "Installation completed!"
echo "Anaconda3 has been installed on your machine."