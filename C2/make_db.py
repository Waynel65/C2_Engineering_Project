from c2_config import db
from c2_database import *

### you will only need to create the database once ###
### if it already exists, it will not be created again ###
### Wayne: for example if you try to make a table with 4 columns, but a table with the same name already exists
### and the existing table only has 3 columns, things will break

# might need to open mysql by using mysql -u root

db.create_all() # create the database
user1 = Client(client_id="wayne", password = "c92bd861b6d2c5d97bb8799c1b8a84b8fff8ffb40e5f62da63aaa372b92c8c95", salt = b'\xfb)8\x82\xfeVu\xfb#\\1\xb1\xed\xb7\x8f\x82\xf6\x0fd\xa2+\x97\xdb\xd3\xe6\xb8\xa3h{\x9e\x9c\x11')
user2 = Client(client_id="yuhao", password = "c92bd861b6d2c5d97bb8799c1b8a84b8fff8ffb40e5f62da63aaa372b92c8c95", salt = b'\xfb)8\x82\xfeVu\xfb#\\1\xb1\xed\xb7\x8f\x82\xf6\x0fd\xa2+\x97\xdb\xd3\xe6\xb8\xa3h{\x9e\x9c\x11')
db.session.add(user1)
db.session.add(user2)
db.session.commit()