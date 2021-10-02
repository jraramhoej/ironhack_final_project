import mysql.connector


def sql_action(query):

    # establish connection to a database
    connection = mysql.connector.connect(user='root', password='18Rj7192!', host='localhost', database='sakila',
                                         auth_plugin='mysql_native_password')

    # try / except (or if statement) to check if connected
    if connection.is_connected():
        print("Connection open.")
    else:
        print("Connection is not successfully open.")

    # define object used to interact with the database
    cursor = connection.cursor()

    # execute query, call cursor to execute
    cursor.execute(query)
    print("Query executed.")

    # commit changes to MySQL
    connection.commit()
    print("Committed to MySQL.")

    # clear the cursor
    cursor.close()
    connection.close()

# create new database
create_database = """CREATE DATABASE IF NOT EXISTS slack;"""

# create reviews table
create_table = """CREATE TABLE IF NOT EXISTS
slack.messages(
client_msg_id VARCHAR PRIMARY KEY,
type TEXT,
reply_users TEXT,
user TEXT,
text TEXT,
ts DATE);"""

# populate tables
def populate_table(df):

    # reviews
    for client_msg_id, type, reply_users, user, text, ts in zip(df["client_msg_id"], df["type"], df["reply_users"], df["user"], df["text"], df["ts"]):

        # define query
        query = "REPLACE INTO slack.messages(client_msg_id, type, reply_users, user, text, ts) VALUES(" + \
        str(client_msg_id) + ", \"" + \
        str(type) + "\", \"" + \
        str(reply_users) + "\", \"" + \
        str(user) + "\", \"" + \
        str(text) + "\", " + \
        "STR_TO_DATE(\"" + str(ts) + "\", \"%Y-%m-%d\"));"

        # execute query
        sql_action(query)

