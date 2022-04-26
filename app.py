
from flask import Flask, render_template
from typing import DefaultDict
from datetime import datetime
##import sqlite3
##from sqlite3 import Error
import mysql.connector
from mysql.connector import Error
import os

DATABASENAME = "inboxProject6"  # PUT THE DATABASE NAME HERE,  when you know it

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
    username = username.upper()

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

        render_template('displayemail.html')
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
    print("Entering composeemail python function")

    # Prompt user for inputs

    #  connect to the SQL db
    connection = create_connection();
    crsr = connection.cursor();


    counter = 0


    # close the connection
    connection.close()
    return "SHOW THIS INFO"
    return

@app.route('/reademail', methods=['POST'])
def reademail(username):
    print("Entering reademail python function")

    email_list = []
    #  connect to the SQL db
    connection = create_connection();
    crsr = connection.cursor();

    try:
        crsr.execute("SELECT from_user, to_user, date, message, time  from messages")
    except:
        print("Debugging - to_user  not found in messages table for", username)
        email_data = "No emails found for " + username
        email_list.append(email_data)
        return email_list


    myresult = crsr.fetchall()
    counter = 0
    for myrow in myresult:
        if username == myrow[1]:

            email_data = "To: " + myrow[1] + " From: " + myrow[0] + " Date: " + myrow[2] + " " + myrow[4] + "\n" + "MSG: " + myrow[3]
            email_list.append(email_data)

    # close the connection
    connection.close()
    return email_list

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database=DATABASENAME
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred trying to connect to sql db {DATABASENAME}")

    return connection


def create_database():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )

    cursor = mydb.cursor()
    stringtoexecute = "CREATE DATABASE " + DATABASENAME
    cursor.execute(stringtoexecute)

    return mydb


def populatesql():
     #This is for testing purposes to populate an SQL db
    cur = None
    try:
        connection = create_database();
    except:
        try:
            connection = create_connection();
        except Error as e:
            print("Could not connect or create database {DATABASENAME}  in populate sql, error is {e}")



    cur = connection.cursor()

    try:
        table = "CREATE TABLE MESSAGES(to_user VARCHAR(32), from_user VARCHAR(32), message VARCHAR(512), date VARCHAR(30),  time VARCHAR(30))"
        cur.execute(table)
        connection.commit()
    except:
        print("messages table already exists in the sql db")


    # Put some messages into the messages table (for testing.
    # This code is just to populate SQL, is not going to be in final project
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    date = now.split(" ")[0]
    time = now.split(" ")[1]
    print("date and time", date, time)

    try:

        cur.executemany("""INSERT INTO messages(date, time, to_user, from_user, message)
        VALUES(%s,%s,%s,%s,%s)""",
            [
                (date, time, "LUKE_S",  "DARTH_V", "Hello Luke I am your Father,  Love from Dad"),
                (date, time,  "LUKE_S", "HAN_S", "Hey Luke, let us grab a beer at The Dickens tomorrow?"),
                (date, time, "DARTH_V", "JRF", "Dear Mr. V,  You suck.   From, Joe F"),
                (date, time, "LUKE_S", "JRF", "Hello Luke, Yes it would be grand to visit.  Joe"),
                (date, time,  "JRF", "DARTH_V", "No, you! -- Darth ")
            ]
        )
    except Error as e:
        print("already created the sql db, - OR - error is ", e)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    app.run(debug=True)
