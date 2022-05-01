"""
    This file stores all the functions that are used to interact with the database from the server
"""

import os
from c2_config import *

### some useful notes here ###
"""
sqlite:///:memory: (in-memory database)
sqlite:///relative_path/test.db (relatie path file-based database)
sqlite:////absolute_path/test.db (abs path file-based database)
"""
# -----------------------------

### configs ###
# APP_KEY = os.environ["APP_KEY"]
password = "ch0nky" # a temperary password to test the server
localhost = "http://127.0.0.1:5000"
template_dir = "../client/templates"
app_secret_key = os.urandom(24)
# -----------------------------

# 3 statuses for a task
CREATED = "CREATED"
TASKED = 'TASKED'
DONE = "DONE"

class Task(db.Model): # a SQLAlchemy class
    id = db.Column(db.Integer, primary_key=True) ## a database entity that allows us to index the entries
    # need to specify length of String if using MySQL; Feel free to change the length
    job_id = db.Column(db.String(288))
    agent_id = db.Column(db.String(288)) ## the agent that is associated with the task
    command_type = db.Column(db.String(288))
    cmd = db.Column(db.String(4096))
    job_status = db.Column(db.String(288))



class Client(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(288))
    password = db.Column(db.String(288))
    # implants = db.relationship("Agent", backref='agent', lazy=True)


class Agent(db.Model): 
    id               = db.Column(db.Integer, primary_key = True)
    agent_id         = db.Column(db.String(288))
    password         = db.Column(db.String(288)) # secret key that verifies the agent with server
    computer_name    = db.Column(db.String(288)) # what computer did it connect from
    username         = db.Column(db.String(80)) # what user are you running as
    GUID             = db.Column(db.String(288)) # computer's GUID
    Integrity        = db.Column(db.String(288)) # what privileges do you have
    ip_address       = db.Column(db.String(32))  # what address did the implant connect from
    session_key      = db.Column(db.String(288)) # after you negotiated a session key, store it per agent
    sleep            = db.Column(db.Float)       # how often does the agent check in 
    jitter           = db.Column(db.Float)       # how random of a check in is it
    first_seen       = db.Column(db.DateTime)    # when did the agent first check in
    last_seen        = db.Column(db.DateTime)    # when was the last time you saw the agent
    expected_checkin = db.Column(db.DateTime)    # when should you expect to see the agent again
    #TODO            : a func to generate a new python datatime for expected checkin

# search agent by agent_id
# link for ref: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
def find_agent_by_id(id_):
    """
        a function that finds an agent in database by its id
    """
    return Agent.query.filter_by(agent_id=id_).first()

def agent_exist(id_):
    """
        a function that checks if an agent exists
    """
    return find_agent_by_id(id_) != None

def find_client_by_id(id_):
    """
        a function that finds a client in database by its id
    """
    return Client.query.filter_by(client_id=id_).first()

def client_exist(id_):
    """
        a function that checks if a client exists
    """
    return find_client_by_id(id_) != None

def find_agent_task(agent_id):
    """
        a function that finds a task for an agent
    """
    return Task.query.filter_by(agent_id=agent_id, job_status= CREATED).first()

def find_task_by_jobID(job_id):
    """
        a function that finds a task by its job_id
    """
    return Task.query.filter_by(job_id=job_id).first()

def hash_passoword(password):
    """
        given a password as a string, return the hashed version
    """
    h = hashlib.sha256()
    h.update(password.encode(encoding='utf-8'))
    hex_password = h.hexdigest()
    return hex_password


def verify_agent_password(reg_agent_id, reg_password):
    """
        a function that verifies the password by comparing
        the hash stored in the database with the hash generated
    """
    hex_password = hash_passoword(reg_password)
    agent = find_agent_by_id(reg_agent_id)
    return agent.password == hex_password

def verify_client_password(reg_client_id, reg_password):
    """
        a function that verifies the password by comparing
        the hash stored in the database with the hash generated
    """
    hex_password = hash_passoword(reg_password)
    client = find_client_by_id(reg_client_id)
    return client.password == hex_password

def list_agents():
    """
        a function that returns a list of agents stored in database
    """
    agents = Agent.query.all()
    agent_ids = [i.agent_id for i in agents]
    return agent_ids

def list_clients():
    """
        a function that returns a list of clients stored in database
    """
    clients = Client.query.all()
    client_ids = [i.client_id for i in clients]
    return client_ids

def list_tasks():
    """
        a function that returns a list of tasks stored in database
    """
    tasks = Task.query.all()
    t = [{"agent_id":i.agent_id, "job_id": i.job_id, "job_status": i.job_status, "command_type": i.command_type, "cmd": i.cmd } for i in tasks]
    return t