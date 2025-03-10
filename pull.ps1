while ($true) {
  $secure_password = Read-Host "Enter password" -AsSecureString
  if ( $secure_password -and $secure_password -ne "") {
    break
  }
}
$password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure_password)
)

try {
  Push-Location $PSScriptRoot


  git fetch origin main
  git reset --hard origin/main

  7z x "transfer.zip" -o"./transfer/" -p"$password" -y

  git fetch origin main
  git reset --hard origin/main

  Remove-Item -Force "transfer.zip"
  Remove-Item -Recurse -Force ".git/logs"
}
finally {
  Pop-Location
}
