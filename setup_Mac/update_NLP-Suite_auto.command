echo "You are about to setup automatic update of the NLP Suite every time you close the NLP Suite, pulling the newest release from GitHub."
echo "The advantage is that you will have to run this command only once."
echo "For this to happen, though, you will need to be connected to the internet."
echo ""

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

git init .
git remote add -t \* -f origin https://github.com/NLP-Suite/NLP-Suite.git
git checkout -f current-stable
git add -A .
git stash

echo
echo "You are set. The NLP Suite will automatically update every time you close the NLP Suite, pulling the newest release from GitHub."
echo