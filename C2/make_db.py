from c2_config import db
from c2_database import *

### you will only need to create the database once ###
### if it already exists, it will not be created again ###
### Wayne: for example if you try to make a table with 4 columns, but a table with the same name already exists
### and the existing table only has 3 columns, things will break

db.create_all() # create the database
me = Client(client_id = 3, password = "35bcb5d1bbb22ee352c0bf79589f953660fa1cef45f696a8c1f2d26d2df54dfa", salt = b'+IE\xa8{\xda\x0cZ\x85\x01\x94\xf9\xc2>\xbc\x90\xa6g_\xb8\xee@bM5\xffu\xa5\x05\xea\xd9\x9a')
db.session.add(me)
db.session.commit()