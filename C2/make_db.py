from c2_server import db

### you will only need to create the database once ###
### if it already exists, it will not be created again ###
### Wayne: for example if you try to make a table with 4 columns, but a table with the same name already exists
### and the existing table only has 3 columns, things will break

db.create_all() # create the database

