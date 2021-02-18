touch ~/.bash_profile
sed -i '' '/alias nlp=/d' ~/.bash_profile
sed -i '' '/alias nlp=/d' ~/.zshrc
echo "alias nlp='source $HOME/anaconda/bin/activate; conda activate NLP; cd "$(cd "$(dirname "$0")"; pwd -P)/../src/"'" >> ~/.bash_profile
echo "alias nlp='source $HOME/anaconda/bin/activate; conda activate NLP; cd "$(cd "$(dirname "$0")"; pwd -P)/../src/"'" >> ~/.zshrc
source ~/.bash_profile
source ~/.zshrc