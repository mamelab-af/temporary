#!/usr/bin/env bash

set -e


read -s -p "Enter password: " password
echo  # 改行を入れる


git fetch origin main
git reset --hard origin/main


unzip -P $password transfer.zip -d ./transfer/


git fetch origin main
git reset --hard origin/main

rm -f transfer.zip
rm -rf .git/logs
