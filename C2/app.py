from c2_database import *
from c2_config import *
from c2_agent import *
from c2_client import *
from c2_task import *

"""
    This is now the c2_server.py file that we used to work on 
    (It is named app.py because flask recognizes this name easier)
"""



# def require_appkey(func):
#     @wraps(func)
#     def decorator(*args, **kwargs):
#         if request.args.get('app_key') and request.args.get('app_key') == APP_KEY:
#             return func(*args, **kwargs)
#         else:
#             print("[-] Missing AppKey or AppKey not match")
#             return jsonify({"status": "authentication failed"})
#     return decorator

def printBytes(data):
    print(data[0:12])
    print(data[12:28])
    print(data[28:])

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        payload = b"\x87\xb8\xa9\xa6\xc2\x39\x42\x5f\xc2\xda\x8c\xc1\xb5\x6a\x9b\x69\x26\x0e\x79\x75\xe5\x81\x29\xe0\x6d\x68\xb3\x62\x1f\xc4\x4d\xa3\x55\xda\x0f\x32\xb6\xd2\x89\x7b\x22"
        return payload
    else:
        message = decrypt_data(request.data) 
        print(type(message))
        print(message)
        return encrypt_data(message)
        
if __name__ == '__main__':
    # HTTPS uses TLS (SSL) to encrypt normal HTTP requests and responses
    # app.run(ssl_context='adhoc') # run with TLS encryption 
    app.run()                      # run without TLS encryption