import sqlite3

from frontend.application.user import User


def create_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(""" CREATE TABLE IF NOT EXISTS users (
        access_token text,
        athlete_id int,
        first_name text,
        last_name text
        )""")
    conn.commit()


def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    out = c.execute("SELECT * FROM users")
    conn.commit()

    if out is not None:
        return out
    return None


def get_user_by_athlete_id():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    out = c.execute("SELECT * FROM users WHERE athlete_id=35492189")

    conn.commit()

    if out is not None:
        return out
    return None


def get_user_by_name(first, last):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    out = c.execute("SELECT * FROM users WHERE first_name=? AND last_name=?", first, last)

    conn.commit()

    if out is not None:
        return out
    return None


def insert_user(access_token, athlete_id, first, last):
    temp = User(access_token, athlete_id, first, last)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if not already_exists(access_token, athlete_id):
        c.execute("INSERT INTO users VALUES (:access_token, :athlete_id, :first, :last)",
                  {'access_token': temp.access_token,
                   'athlete_id': temp.athlete_id,
                   'first': temp.first,
                   'last': temp.last})

        conn.commit()
        return "verified"

    return "User is already authorised"


def already_exists(access_token, athlete_id):
    for user in get_users():
        if user[1] == athlete_id or user[0] == access_token:
            return True
    return False

