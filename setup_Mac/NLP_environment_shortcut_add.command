touch ~/.bash_profile
sed -i '' '/alias NLP=/d' ~/.bash_profile
sed -i '' '/alias NLP=/d' ~/.zshrc
echo "alias NLP='source $HOME/anaconda/bin/activate; conda activate NLP; cd "$(cd "$(dirname "$0")"; pwd -P)/../src/"'" >> ~/.bash_profile
echo "alias NLP='source $HOME/anaconda/bin/activate; conda activate NLP; cd "$(cd "$(dirname "$0")"; pwd -P)/../src/"'" >> ~/.zshrc
source ~/.bash_profile
source ~/.zshrc