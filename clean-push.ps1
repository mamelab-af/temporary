try {
  Push-Location $PSScriptRoot

  git checkout --orphan new_main

  git add .

  git commit -m "Initial commit"
  git branch -D main
  git branch -m main
  git push origin -f main

  Start-Sleep -Seconds 60

  git checkout --orphan new_main

  git rm --cached -r .
  git add .gitignore
  git add clean-push.sh
  git add clean-push.ps1
  git add force-pull.sh
  git add force-pull.ps1

  git commit -m "Initial commit"
  git branch -D main
  git branch -m main
  git push origin -f main

  Remove-Item -Recurse -Force .git/logs
}
finally {
  Pop-Location
}