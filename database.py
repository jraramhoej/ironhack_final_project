import mysql.connector

# connect to MySQL
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
type TEXT,
reply_users TEXT,
user VARCHAR(255),
reactions TEXT,
text TEXT,
ts VARCHAR(255),
date TEXT,
PRIMARY KEY (user,ts));"""

# populate tables
def populate_table(df):

    # reviews
    for type, reply_users, user, reactions, text, ts, date in zip(df["type"], df["reply_users"], df["user"], df["reactions"], df["text"], df["ts"], df["date"]):

        # define query
        query = "REPLACE INTO slack.messages(type, reply_users, user, reactions, text, ts, date) VALUES(\"" + \
        str(type) + "\", \"" + \
        str(reply_users) + "\", \"" + \
        str(user) + "\", \"" + \
        str(reactions) + "\", \"" + \
        str(text) + "\", \"" + \
        str(ts) + "\", \"" + \
        str(date) + "\");"
        #"STR_TO_DATE(\"" + str(ts) + "\", \"%Y-%m-%d\"));"

        # execute query
        sql_action(query)

# connect to MySQL
def sql_retrieve(query):

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

    # get results if retrieving data
    results = cursor.fetchall()

    # description of results
    description = cursor.description

    # commit changes to MySQL
    connection.commit()
    print("Committed to MySQL.")

    # clear the cursor
    cursor.close()
    connection.close()

    return {"results": results, "description": description}

# get all data from MYSQL
retrieval = "SELECT * FROM slack.messages;"
