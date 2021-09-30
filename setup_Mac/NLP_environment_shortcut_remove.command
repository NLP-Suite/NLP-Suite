while true; do
    read -p "You are removing the NLP shortcut. Do you wish to continue? [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done


sed -i '' '/alias NLP=/d' ~/.bash_profile
sed -i '' '/alias nlp=/d' ~/.bash_profile
sed -i '' '/alias NLP=/d' ~/.zshrc
sed -i '' '/alias nlp=/d' ~/.zshrc
unalias NLP
unalias nlp