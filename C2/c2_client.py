"""
    this file stores all the functions that are used to interact with the tasks from the server
"""
from c2_config import *
from c2_database import *


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
# @require_appkey
def login_client():
    """
        listens to the /register_client route
        and processes the registration request from clients
    """

    client_id = request.form.get('client_id')
    client_password = request.form.get('password')
    if client_id == None or client_password == None:
        return jsonify({"status": "failed to get data from client"})
    if not client_exist(client_id):
        client = Client(client_id=client_id, password=hash_passoword(client_password))
        db.session.add(client)
        db.session.commit()

    #TODO: need to change this part so that password is properly verified
    if verify_client_password(client_id, client_password):
        print(f"[+] a new client has successfully registered: {client_id}")
        # flask.flash(f"Welcome {client.client_id}!")
        client = find_client_by_id(client_id)
        client.authenticated = True
        login_user(client) ## user loader function from flask-login

        return redirect(url_for("dashboard")) # redirect to the home page
    else:
        print("[-] authentication failed")
        return render_template("unauthorized.html")
    
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