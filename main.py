from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
from workout import Workout
from user import User

app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()
    c.execute("""DELETE FROM users WHERE id=:userid""", {"userid": user_id})
    print(c.fetchall())
    conn.commit()
    conn.close()
    return redirect(url_for('viewallusers', user_is_deleted=True))


@app.route('/login')
def login():
    if 'wrong_action' in request.args:
        show_msg = True
        msg = "Wrong username/password!"
    else:
        show_msg = False
        msg = ""
    return render_template('login.html', show_msg=show_msg, msg=msg)


def get_connected_user(db_cursor):
    if 'user' in request.cookies:
        user_id = request.cookies['user']
        db_cursor.execute("""SELECT * FROM users WHERE id=:user_id""", {'user_id': user_id})
        row = db_cursor.fetchone()
        if row is None:
            return None
        else:
            user = User(row[1], row[2], row[3], user_id=row[0])
            return user
    return None



@app.route('/login_data', methods=['POST'])
def login_data():
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()
    username = request.form['username']
    password = request.form['password']

    c.execute("SELECT * FROM users WHERE username = :username AND password = :password",
              {'username': username, 'password': password})
    row = c.fetchone()
    if row is None:
        return redirect(url_for('login', wrong_action=True))
    else:
        user_id = row[0]
        resp = make_response(redirect(url_for('index', correct_action=True)))
        resp.set_cookie('user', user_id, max_age=3600)
        return resp


@app.route('/viewAllUsers')
def viewallusers():
    if 'user_is_added' in request.args:
        show_msg = True
        msg = "Your user has been added!"
    elif 'user_is_deleted' in request.args:
        show_msg = True
        msg = "Your user has been deleted!"
    else:
        show_msg = False
        msg = ""

    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()

    connected_user = get_connected_user(c)
    is_connected, username = get_is_connected_and_name(connected_user)

    c.execute("SELECT * FROM users ORDER BY username")

    rows = c.fetchall()
    users = []

    for row in rows:
        c = User(row[1], row[2], row[3], user_id=row[0])
        users.append(c)
    return render_template('viewAllUsers.html', users=users, show_msg=show_msg, msg=msg, is_connected=is_connected,
                           username=username)


@app.route('/signOut')
def signout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('user', "", expires=0)
    return resp


@app.route('/index')
def index():
    if 'is_sent' in request.args:
        show_msg = True
        msg = "Your workout has been added!"
    elif 'is_deleted' in request.args:
        show_msg = True
        msg = "Your workout has been removed!"
    elif "is_edited" in request.args:
        show_msg = True
        msg = "Your workout has been updated!"

    elif "user_created" in request.args:
        show_msg = True
        msg = "Your user has been created!"

    elif "user_is_deleted" in request.args:
        show_msg = True
        msg = "The user has been deleted!"
    elif 'correct_action' in request.args:
        show_msg = True
        msg = "You are now connected!"
    else:
        show_msg = False
        msg = ""

    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()

    connected_user = get_connected_user(c)
    is_connected, username = get_is_connected_and_name(connected_user)

    if not is_connected:
        return render_template('index.html', show_msg=show_msg, msg=msg, is_connected=is_connected,
                               username=username)
    c.execute("SELECT * FROM workouts WHERE user_id = :connected_user", {"connected_user" : connected_user.user_id})
    rows = c.fetchall()
    workouts = []

    for row in rows:
        c = Workout(row[1], row[2], row[3], row[4], row[5], row[6], id=row[0])
        workouts.append(c)

    return render_template('index.html', workouts=workouts, show_msg=show_msg, msg=msg, is_connected=is_connected,
                           username=username)


def get_is_connected_and_name(connected_user):
    if connected_user is None:
        is_connected = False
        username = ""
    else:
        is_connected = True
        username = connected_user.username
    return is_connected, username


@app.route('/newWorkout')
def form():
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()
    connected_user = get_connected_user(c)
    is_connected, username = get_is_connected_and_name(connected_user)
    return render_template('newWorkout.html', is_connected=is_connected, username=username)


@app.route('/changeUser')
def change_user():
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()
    connected_user = get_connected_user(c)
    is_connected, username = get_is_connected_and_name(connected_user)
    return render_template('changeUser.html', is_connected=is_connected, username=username)


@app.route('/user_data', methods=['POST'])
def user_data():
    if "user_id" not in request.form:
        conn = sqlite3.connect('mydb.db')
        c = conn.cursor()

        user = User(request.form['username'], request.form['password'], request.form['email'])
        c.execute("""INSERT INTO users VALUES(:user_id, :username, :password, :email)""",
                  {"user_id": user.user_id, "username": user.username, "password": user.password, "email": user.email})
        conn.commit()
        conn.close()
        return redirect(url_for('viewallusers', user_is_added=True))


@app.route('/form_data', methods=['POST'])
def form_data():
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()
    if "id" in request.form:
        user_id = request.cookies['user']
        c1 = Workout(request.form['name'], request.form['description'], request.form['length'],
                     request.form['video'], request.form['type'], user_id, id=request.form['id'])

        print(c1.id, c1.description)

        c.execute("""UPDATE workouts
            SET name = :name, description = :description, length = :length, video_url= :video_url, type = :type
            WHERE id = :id
        """, {"name": c1.name, "description": c1.description, "length": c1.length, "video_url": c1.video_url,
              "type": c1.type, "id": c1.id})
        conn.commit()
        conn.close()
        return redirect(url_for('index', is_edited=True))
    else:
        user_id = request.cookies['user']

        c1 = Workout(request.form['name'], request.form['description'], request.form['length'], request.form['video'],
                     request.form['type'], user_id)
        c.execute("""INSERT INTO workouts VALUES(:id, :name, :description, :length, :video_url, :type, :user_id)""",
                  {"id": c1.id, "name": c1.name, "description": c1.description, "length": c1.length,
                   "video_url": c1.video_url, "type": c1.type, "user_id": c1.user_id})
        conn.commit()
        conn.close()
        return redirect(url_for('index', is_sent=True))


@app.route('/editWorkout/<id>')
def edit_workout(id):
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM workouts WHERE id=:id""", {"id": id})
    row = c.fetchone()
    c1 = Workout(row[1], row[2], row[3], row[4], row[5], row[6], id=row[0])
    conn.close()
    return render_template('editWorkout.html', workout=c1)


@app.route("/delete/<id>")
def delete_workout(id):
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()
    c.execute("""DELETE FROM workouts WHERE id=:id""", {"id": id})
    conn.commit()
    conn.close()

    return redirect(url_for('index', is_deleted=True))


if __name__ == '__main__':
    app.run()
