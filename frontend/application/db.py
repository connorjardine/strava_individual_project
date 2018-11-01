import sqlite3

from frontend.application.user import User


# conn = sqlite3.connect('users.db')
# c = conn.cursor()
# c.execute("ALTER TABLE users ADD password text")
# conn.commit()

# conn.close()

def create_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(""" CREATE TABLE IF NOT EXISTS users (
        access_token text,
        athlete_id int,
        first_name text,
        last_name text,
        username text,
        password text
        )""")
    conn.commit()


# Returns a list of users
def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    out = c.execute("SELECT * FROM users")
    conn.commit()

    if out is not None:
        return out.fetchall()
    return None


# Returns a tuple
def get_user_by_athlete_id(athlete_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    out = c.execute("SELECT DISTINCT * FROM users WHERE athlete_id=?", (athlete_id,))

    conn.commit()

    if out is not None:
        return out.fetchall()[0]
    return None

# Returns a tuple
def get_user_by_username(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    out = c.execute("SELECT DISTINCT * FROM users WHERE username=?", (username,))

    conn.commit()

    if out is not None:
        return out.fetchall()[0]
    return None


def insert_user(access_token, athlete_id, first, last, password, username):
    temp = User(access_token, athlete_id, first, last, password, username)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if not already_exists(athlete_id):
        c.execute("INSERT INTO users VALUES (:access_token, :athlete_id, :first, :last, :password, :username)",
                  {'access_token': temp.access_token,
                   'athlete_id': temp.athlete_id,
                   'first': temp.first,
                   'last': temp.last,
                   'username' : temp.username,
                   'password': temp.password})

        conn.commit()
        return "verified"

    return "User is already authorised"


def already_exists(athlete_id):
    for user in get_users():
        if user[1] == athlete_id:
            return True
    return False



