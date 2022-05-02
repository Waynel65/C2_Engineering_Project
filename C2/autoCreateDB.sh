# mysql -uroot --password=<mypassword> -e "DROP DATABASE c2_server;"
# Use the line above to pass in your password
mysql -uroot -e "DROP DATABASE c2_server;"
mysql -uroot -e "CREATE DATABASE c2_server;"
python make_db.py 