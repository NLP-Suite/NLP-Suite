cd "$(dirname "$0")/.."
git init .
git remote add -t \* -f origin https://github.com/NLP-Suite/NLP-Suite.git
git checkout -f current-stable
git add -A .
git stash