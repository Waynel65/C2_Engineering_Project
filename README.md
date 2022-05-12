# C2_Engineering_Project

## C2 Folder: ##

- Contains all the files related to the server side of the project

- To run the c2 server

    0. Make sure you have python3 installed
    1. cd into the C2 folder
    2. Create a virtual environtment with `python3 -m venv c2_env`
    3. Acticate the virtual environment with `source c2_env/bin/activate`, or `c2_env/Scripts/activate` if you are using powershell
    4. You can exit the virtual environtment with `deactivate`
    5. Install the dependencies with `pip3 install -r requirements.txt`
    6. Create a new database called `c2_server` in mysql by using `CREATE DATABASE c2_server`
    7. Create a new file in the C2 folder named `creds.py` with the line `db_cred = {"username":"", "password":""}`, and fill in your username and password for your mysql server
    8. Create a database with `python3 make_db.py`
    9. Run the server with `flask run`

- After installing new dependencies, run `pip3 freeze > requirements.txt`

## implant Folder:

- To compile, run `make implant`
<<<<<<< HEAD
- Double click `implant.exe` to run the implant in default mode and connect to the remote server
- For development/testing purposes, you can run `implant.exe -local` to connect to your local server and view implant behavior in the console window 

=======
- To run the implant, run `./bin/implant.exe`
- Function 'stealer()' in chrome.cpp implements the stealer
- Static compile is needed.
>>>>>>> 952e7aa3d64a0645c30c748639c073fc79c6bb48
