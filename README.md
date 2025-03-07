# Secure Transfer

It temporarily uploads a file, waits a few seconds, then deletes the uploaded file, as well as the commit history and logs.  
That's it ✌️

## How to use

1. Put files

    Please put the files you want to upload in the `transfer` folder.

2. Push

    1. Run script

       - `pushp.ps1` or `pushp.sh` ... The password is the value entered by the user.
       - `pushu.ps1` or `pushu.sh` ... password is the uuid.

    2. Please enter the password for the zip file.

    3. Zip the transfer folder with a password, commit it to the `main` branch, and push it.

    4. Wait the number of seconds specified by the `-s` or `--sleep` option. If not specified, wait 60 seconds.

    5. Delete the commit history of the `main` branch, include only the following files in staging, commit and push again:

        - `transfer/.gitkeep`
        - `.gitignore`
        - `pull.ps1`
        - `pull.sh`
        - `pushp.ps1`
        - `pushp.sh`
        - `pushu.ps1`
        - `pushu.sh`
        - `README.md`

    6. Delete `transfer.zip` and everything under `.git/logs`.

3. Pull

    1. Run `pull.ps1` or `pull.sh`

    2. Please enter the password for the zip file.

    3. Pull from the `main` branch.

    4. Extract the contents of the zip file into the `transfer` folder.

    5. Pull from the `main` branch again.

    6. Delete `transfer.zip` and everything under `.git/logs`.
