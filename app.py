
from flask import Flask, render_template
from typing import DefaultDict
from datetime import datetime
import sqlite3
from sqlite3 import Error
import os


project_root = os.path.dirname(__file__)
# define the templates directory where you keep your html files that get rendered
template_pathFlask = os.path.join(project_root, 'templates')
app = Flask(__name__, template_folder=template_pathFlask)
app.secret_key = "27eduCBA09"


READEMAIL, SENDEMAIL, CHECKEMAIL, CREATESQL_FOR_TESTING = "reade", "sende", "checke", "createsql"
AVAILABLE_COMMANDS = {
    'ReadEmail': READEMAIL,
    'SendEmail': SENDEMAIL,
    'CheckEmailUpdates': CHECKEMAIL,
    'CreateSQL': CREATESQL_FOR_TESTING
}
# Define your routes

@app.route('/')
@app.route('/execute', methods=['GET', 'POST'])
def execute():
    return render_template("main.html", commands=AVAILABLE_COMMANDS)


@app.route('/<cmd>')
def command(cmd=None):
    # main.html  has user select a command, to read email, write email, etc.  Process the command.
    username = cmd.split(")(")[0]  # Use the parens as a separator (cos users unlikely to have )( in their user name
    cmd = cmd.split(")(")[1]
    if cmd == READEMAIL:
        response = "Reading email for " + username

        email_list = reademail(username)
        return render_template('displayemail.html', email_list=email_list)

    elif cmd == CREATESQL_FOR_TESTING:
        response = "Creating sql for testing - TEST ONLY, not for production"
        populatesql()
        return response, 200, {'Content-Type': 'text/plain'}
    elif cmd == SENDEMAIL:
        response = "Compose a new email"
        composeemail(username)
        return response, 200, {'Content-Type': 'text/plain'}
    elif cmd == CHECKEMAIL:
        response = "Checking for new email for " + username
        return response, 200, {'Content-Type': 'text/plain'}
    else:
        cmd = cmd[0].upper()
        response = "This option is not currently working"
        return response, 200, {'Content-Type': 'text/plain'}

@app.route('/composeemail', methods=['POST'])
def composeemail(username):
    #TODO - write this function
    return

@app.route('/reademail', methods=['POST'])
def reademail(username):
    print("Entering reademail python function")
    username = username.upper()
    #  connect to the SQL db
    try:
        connection = sqlite3.connect("inboxProject3.db")  # TODO FIND db name and location?
        # set up our cursor to that db
        crsr = connection.cursor()
    except Error as e:
        # If we could not connect to the sql, give a nice error and stop
        print("Could not attach to the db", e)
        return "Could not connect to the email database, please try again later"
    try:
        crsr.execute("SELECT * FROM messages")
        connection.commit()
        # print(crsr.fetchall())  # This is a debugging statement to make sure tables exist in the sql database/file
    except Error as e:
        print("no tables in the db to list", e)
    try:
        crsr.execute("SELECT from_user, to_user, date, message, time  from messages")
    except Error as e:
        print("Debugging - to_user  not found in messages table for", username, e)
        return "Could not locate to_user name in the database"
    response = "No emails found for " + username
    email_list = []
    myresult = crsr.fetchall()
    counter = 0
    for myrow in myresult:
        if username == myrow[1]:
            '''email_dict[counter] = []
            email_dict[counter].append(("TO:" + myrow[1]))
            email_dict[counter].append(("FROM:" + myrow[0]))
            email_dict[counter].append(("Date:" + myrow[2]))
            email_dict[counter].append(myrow[3])
            print("Debugging - hit line 97", email_dict[counter])
            counter = counter + 1'''
            email_data = "To: " + myrow[1] + " From: " + myrow[0] + " Date: " + myrow[2] + " " + myrow[4] + "\n" + "MSG: " + myrow[3]
            email_list.append(email_data)

    # close the connection
    connection.close()
    return email_list


def populatesql():
    """ This is for testing purposes to populate an SQL db"""
    conn = None
    try:
        conn = sqlite3.connect("inboxProject3.db")
    except Error as e:
        print(e)
    cur = conn.cursor()
    try:
        table = """CREATE TABLE MESSAGES(to_user VARCHAR(32), from_user VARCHAR(32), message VARCHAR(512), 
        date VARCHAR(30),  time VARCHAR(30));"""
        cur.execute(table)
        conn.commit()
    except Error as e:
        print(e)
        print("messages table exists")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Did messages get created?")
    print(cur.fetchall())  # This is a debuggin statement to make sure tables exist in the sql database/file

    try:
        cur.execute("SELECT * FROM messages")
        conn.commit()
        print(cur.fetchall())  # This is a debugging statement to make sure tables exist in the sql database/file
    except Error as e:
        print("no tables in the db to list", e)

    # Put some messages into the messages table (for testing.
    # This code is just to populate SQL, is not going to be in final project
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    date = now.split(" ")[0]
    time = now.split(" ")[1]
    print("date and time", date, time)

    try:
        cur.executemany("INSERT INTO messages (date, time, to_user, from_user, message) VALUES (?, ?, ?, ?, ?)",
            [
                (date, time, "LUKE_S",  "DARTH_V", "Hello Luke I am your Father"),
                (date, time,  "JRF", "LUKE_S", "Hey Joe, want to go flying to Gondor tomorrow?"),
                (date, time, "DARTH_V", "JRF", "Dear Mr. Vader,   You suck.   Love, Joe F"),
                (date, time,  "LUKE_S", "JRF", "Hello Luke, Yes it would be grand to visit.  Joe")
            ]
        )
    except Error as e:
        print("already created the sql db, error is ", e)

    conn.commit()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")

    print(cur.fetchall())  # This is a debuggin statement to make sure tables exist in the sql database/file
    conn.close()


if __name__ == "__main__":
    app.run(debug=True)
