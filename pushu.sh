#!/usr/bin/env bash

set -e

while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -s)
      sleep_duration="$2"
      shift 2  # -s と値を消費
      ;;
    --sleep)
      sleep_duration="$2"
      shift 2  # --sleep と値を消費
      ;;
    *)
      echo "Unknown option: $1"
      shift
      ;;
  esac
done

if [[ -z "$sleep_duration" || "$sleep_duration" -le 0 ]]; then
  sleep_duration=60
fi


uuid=$(uuidgen)

cd transfer/
zip -P $uuid -r ../transfer.zip *
cd -


git checkout --orphan new_main

git add transfer/.gitkeep
git add .gitignore
git add pushp.ps1
git add pushp.sh
git add pushu.ps1
git add pushu.sh
git add pull.ps1
git add pull.sh
git add README.md
git add transfer.zip

git commit -m "Initial commit"
git branch -D main
git branch -m main
git push origin -f main


echo "sleeping $sleep_duration ..."
echo "Password: \"$uuid\""
sleep $sleep_duration


# rm -rf transfer/*
# touch transfer/.gitkeep
rm -f transfer.zip

git checkout --orphan new_main

git rm --cached -r .
git add transfer/.gitkeep
git add .gitignore
git add pushp.ps1
git add pushp.sh
git add pushu.ps1
git add pushu.sh
git add pull.ps1
git add pull.sh
git add README.md

git commit -m "Initial commit"
git branch -D main
git branch -m main
git push origin -f main

rm -rf .git/logs
