import sqlite3

from frontend.application.user import User

conn = sqlite3.connect('codes.db')

c = conn.cursor()

# c.execute(""" CREATE TABLE users (
#           first text,
#           last text,
#           code text
#          )""")

conn.commit()

temp = User('Chris', 'Browning', '123456777')
c.execute("INSERT INTO users VALUES (:first, :last, :code)", {'first': temp.first, 'last': temp.last, 'code': temp.code})
conn.commit()

conn.close()


def return_users():
    conn = sqlite3.connect('codes.db')

    c = conn.cursor()

    c.execute("SELECT * FROM users")

    out = c.fetchall()

    conn.commit()

    conn.close()

    return out

