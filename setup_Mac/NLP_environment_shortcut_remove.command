echo "You are about to remove the NLP shortcut that 1. activates the NLP environment and 2. changes directory to the NLP installation directory by simply typing NLP in command line/prompt."
echo
while true; do
    read -p "Do you wish to continue? [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Remove Aborted." && exit;;
        * ) echo "Please answer yes or no.";;
    esac
done


sed -i '' '/alias NLP=/d' ~/.bash_profile
sed -i '' '/alias nlp=/d' ~/.bash_profile
sed -i '' '/alias NLP=/d' ~/.zshrc
sed -i '' '/alias nlp=/d' ~/.zshrc
unalias NLP
unalias nlp

echo
echo "The NLP shortcut has been removed."
echo "Double click on STEP3-NLP-environment.bat to add again the NLP shortcut."