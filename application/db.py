import sqlite3

conn = sqlite3.connect('codes.db')

c = conn.cursor()

# c.execute(""" CREATE TABLE users (
#           first text,
#           last text,
#           code text
#          )""")

#temp = User('David', 'Browning', '123456777')
#c.execute("INSERT INTO users VALUES (:first, :last, :code)", {'first': temp.first,'last': temp.last, 'code': temp.code})
#conn.commit()


def return_users():
    c.execute("SELECT * FROM users")

    out = c.fetchall()
    print(out)

    conn.commit()

    conn.close()

    return out
