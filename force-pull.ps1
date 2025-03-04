try {
  Push-Location $PSScriptRoot

  git fetch origin main
  git reset --hard origin/main

  Start-Sleep -Seconds 60

  git fetch origin main
  git reset --hard origin/main

  Remove-Item -Recurse -Force .git/logs
}
finally {
  Pop-Location
}