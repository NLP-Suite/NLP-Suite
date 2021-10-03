echo "You are about to update the NLP Suite pulling the newest release from GitHub."
echo "For this to happen, though, you need to be connected to the internet."
echo "You could use the update_NLP Suite_auto.bat to automatically update every time you close the NLP Suite, pulling the newest release directly from GitHub. The advantage is that you will have to run this command only once."
echo

while true; do
    read -p "Do you wish to continue? [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Update Aborted." && exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

cd "$(dirname "$0")/.."

if ! command -v git &> /dev/null
then
    echo "git could not be found"
    export CI=1
    echo | ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew install git
fi

git add -A .
git stash
git pull -f origin current-stable

echo
echo "You have updated the NLP Suite to the latest release available on GitHub."