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
    return Client.query.get(user_id)

@app.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route('/client/login', methods=["GET","POST"])
def login_client():
    """
        listens to the /register_client route
        and processes the registration request from clients
    """

    client_id = request.form.get('client_id')
    client_password = request.form.get('password')
    if client_id == None or client_password == None:
        return jsonify({"status": "failed to get data from client"})
    client = find_client_by_id(client_id)
    # if not client_exist(client_id):
    #     hashed_password, salt = hash_password(client_password)
    #     client = Client(client_id=client_id, password=hashed_password, salt=salt)
    #     db.session.add(client)
    #     db.session.commit()

    #TODO: need to change this part so that password is properly verified
    if verify_client_password(client_id, client_password):
        print(f"[+] a new client has successfully registered: {client_id}")
        # flask.flash(f"Welcome {client.client_id}!")
        client = find_client_by_id(client_id)
        client.authenticated = True
        login_user(client) ## user loader function required from flask-login
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
    # client_list = list_clients() # a list of clients that are stored in the database
    # task_list = list_tasks() # a list of tasks that are stored in the database
    # info = jsonify({"agents": agent_list, 
    #                 "clients": client_list,
    #                 "tasks": task_list})

    return render_template("dashboard.html", info=agent_list)
    
    # return info

@app.route('/client/operation', methods=['GET', 'POST'])
def operation():
    """
        listens to the /operation route
        This page should show all the agents & operators connected to the server
    """
    agent_id = request.form.get('agent_id')
    print("agent_id: ", agent_id)
    if agent_id == None:
        ## second attempt to get agent_id from redirecting (from task_create in c2_task.py) => bad design, sorry
        agent_id = request.args.get('agent_id')
        print("agent_id: ", agent_id)
        if agent_id == None:
            return jsonify({"status": "failed to get data from client"})

    # print("agent_id:", agent_id)
    task_list = list_tasks(agent_id) # a list of tasks belonged to this agent
    if task_list == None or len(task_list) == 0:
        print("[-] no task found for agent:", agent_id)
        return render_template("operation.html", agent_id=agent_id, tasks=[])
    else:
        # print("task_list:", task_list)
        return render_template("operation.html", agent_id=agent_id, tasks=task_list)
    

@app.route('/client/logout', methods=['GET'])
# @login_required
def logout():
    pass