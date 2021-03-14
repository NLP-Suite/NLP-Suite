cd "$(dirname "$0")/.."

if ! command -v git &> /dev/null
then
    echo "git could not be found"
    export CI=1
    echo | ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew install git
fi

git pull -f origin current-stable
