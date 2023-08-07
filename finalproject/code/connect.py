import MySQLdb

# Load configuration from appconfig.json
SQL_HOST = "database2.c5qodmqginry.us-east-2.rds.amazonaws.com"
SQL_USER = "root"
SQL_PASSWORD = "nick1234"
SQL_DB = "UserDB"

# Create a connection to the database
try:
    conn = MySQLdb.connect(host=SQL_HOST, user=SQL_USER, passwd=SQL_PASSWORD, db=SQL_DB).cursor(MySQLdb.cursors.DictCursor)
    conn.execute("Select * from userdata")
    print("Connected to the database!")
except MySQLdb.Error as e:
    print(f"Error connecting to the database: {e}")
