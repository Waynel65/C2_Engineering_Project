from c2_database import *
from c2_config import *
from c2_agent import *
from c2_client import *
from c2_task import *





# def require_appkey(func):
#     @wraps(func)
#     def decorator(*args, **kwargs):
#         if request.args.get('app_key') and request.args.get('app_key') == APP_KEY:
#             return func(*args, **kwargs)
#         else:
#             print("[-] Missing AppKey or AppKey not match")
#             return jsonify({"status": "authentication failed"})
#     return decorator


if __name__ == '__main__':
    # HTTPS uses TLS (SSL) to encrypt normal HTTP requests and responses
    # app.run(ssl_context='adhoc') # run with TLS encryption 
    app.run()                      # run without TLS encryption