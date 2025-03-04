#!/usr/bin/env bash

git fetch origin main
git reset --hard origin/main

sleep 60s

git fetch origin main
git reset --hard origin/main

rm -rf .git/logs
