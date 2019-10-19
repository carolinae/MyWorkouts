import sqlite3

conn = sqlite3.connect('mydb.db')
c = conn.cursor()

c.execute("""CREATE TABLE workouts(
            id text, name text, description text, length integer, video_url text, type text, user_id text
)""")

c.execute("""CREATE TABLE users(
            id text, username text, password integer, email text
)""")

conn.commit()
conn.close()


