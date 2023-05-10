echo "STEP1 will install Anaconda3 on your machine. If these applications are already installed on your machine, the script will exit."
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
done
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


if test -f $HOME/opt/anaconda3/bin/activate; then
    source $HOME/optanaconda/bin/activate
    conda init/
    conda init zsh
    exit 0
fi

echo "I am detecting the version of the system.... which is"
echo $(uname -m)
processor=$(uname -m)

if [[ "$processor" == "arm64" ]]; then
    echo "I have detected your program is in M1, M2, M1 Pro or M2 Pro. If it is WRONG, please CTRL+C."
    curl -o anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2022.10-MacOSX-arm64.sh
else
    echo "I have detected your program is in INTEL. If it is WRONG, please CTRL+C."
    curl -o anaconda.sh https://repo.anaconda.com/archive/Anaconda3-2022.10-MacOSX-x86_64.pkg
fi

bash anaconda.sh -b -y -p $HOME/anaconda
source $HOME/anaconda/bin/activate
conda init
conda init zsh
echo "Installation completed!"
echo "Anaconda3 has been installed on your machine."