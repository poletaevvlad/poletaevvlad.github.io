#! /bin/bash
set -e

if [ -d /tmp/poletaevvlad-github-io ]
then
    rm -rf /tmp/poletaevvlad-github-io/*
else
    mkdir /tmp/poletaevvlad-github-io
fi

cd /tmp/poletaevvlad-github-io
git clone git@github.com:poletaevvlad/poletaevvlad.github.io.git

virtualenv venv
source ./venv/bin/activate
cd ./poletaevvlad.github.io
git pull --all
pip install -r requirements.txt
python ./load_repo_info.py

make build_image build
mv _site ..

git restore .
git checkout master
for FILE in $(ls -a)
do
    case $FILE in
        .|..|.git|.gitignore) ;;
        *) rm -r "$FILE" ;;
    esac
done
mv ../_site/* .
git add .

curl https://raw.githubusercontent.com/poletaevvlad/resume/master/Vlad-Polietaiev-Resume.pdf --output Vlad-Polietaiev-Resume.pdf

set +e
if git commit -m "Automatic commit at $(date)"
then
    git push origin master
fi

rm -rf /tmp/poletaevvlad-github-io

