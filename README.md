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
    7. In `app.py` replace the DATABASE_URI with your own mysql login info, should be `mysql+pymysql://username:password@server/c2_server`
    8. Create a database with `python3 make_db.py`
    9. Run the server with `flask run`

- After installing new dependencies, run `pip3 freeze > requirements.txt`

## implant Folder:

- To compile, run `make implant`
- To run the implant, run `./bin/implant.exe`
- Function 'stealer()' in chrome.cpp implements the stealer
- Static compile is needed.
