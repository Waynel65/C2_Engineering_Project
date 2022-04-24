from flask import Flask , request, jsonify, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy ## inherently handles syncronization for us ##
from sqlalchemy import Column, Integer, String, ForeignKey, Table
import hashlib



# some useful notes here #
"""
sqlite:///:memory: (in-memory database)
sqlite:///relative_path/test.db (relatie path file-based database)
sqlite:////absolute_path/test.db (abs path file-based database)
"""
###############################



# configs
password = "ch0nky" # a temperary password to test the server
localhost = "http://127.0.0.1:5000"
template_dir = "../client/templates"

# code snippets from lecture13

CREATED = "CREATED"
TASKED = 'TASKED'
DONE = "DONE"

app = Flask(__name__, template_folder=template_dir) # use this to generate routes and handlers
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c2_db.sqlite' # set the database to work with flask
db = SQLAlchemy(app)

class Task(db.Model): # a SQLAlchemy class
    id = db.Column(db.Integer, primary_key=True) ## a database entity that allows us to index the entries
    job_id = db.Column(db.String)
    command_type = db.Column(db.String)
    cmd = db.Column(db.String)
    Status = db.Column(db.String)
    agent_id = db.Column(db.String)

class Agent(db.Model): # a SQLAlchemy class
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String)
    password = db.Column(db.String)

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

    if verify_password(reg_agent_id, reg_password):
        print("[+] a new agent has successfully registered")
        print(f"[+] agent_id: {reg_agent_id}")
    else:
        # print("[-] authentication failed")
        return jsonify({"status": "authentication failed"})

    print(f"[+] A new agent {agent.id} has connected to our server! {agent.agent_id}, {agent.username}")

    return jsonify({"status": "ok", "message": "Welcome!"})

@app.route("/")
def home():
    return render_template("login.html")

@app.route('/login_client', methods=['POST'])
def login_client():
    """
        listens to the /register_client route
        and processes the registration request from clients
    """

    try:
        client_id = request.form.get('client_id')
        client_password = request.form.get('password')
        #TODO: check password here
        print(f"[+] client_id: {client_id}, client_password: {client_password}")
        return redirect(url_for("dashboard")) # redirect to the home page
    except:
        print("[-] client registration failed")
        return render_template("unauthorized.html")
    
    ## check userID and password
    ## if correct, grant access to home page
    
    return ""

@app.route('/dashboard', methods=['GET'])
def home_page():
    """
        Listens to the /dashboard route
        This page should show all the agents & operators connected to the server
        
    """
    return "welcome to dashboard!"
    


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

if __name__ == '__main__':
    app.run()