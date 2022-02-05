echo "You are about to setup a shortcut that by typing NLP in command line/prompt will 1. activate the NLP python environment and 2. change the directory to the NLP/src directory."
echo
while true; do
    read -p "Do you wish to continue? [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Setup Aborted." && exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

touch ~/.bash_profile
sed -i '' '/alias NLP=/d' ~/.bash_profile
sed -i '' '/alias NLP=/d' ~/.zshrc
echo "alias NLP='conda activate NLP; cd "$(cd "$(dirname "$0")"; pwd -P)/../src/"'" >> ~/.bash_profile
echo "alias NLP='conda activate NLP; cd "$(cd "$(dirname "$0")"; pwd -P)/../src/"'" >> ~/.zshrc
source ~/.bash_profile
source ~/.zshrc

echo
echo "The NLP shortcut has been added to the environment variables."
echo "Double click on NLP_environment_shortcut_remove.bat to remove the shortcut."
