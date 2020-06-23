import os
from functools import wraps
from datetime import datetime

from flask import Flask, session, render_template, request, redirect
from flask_socketio import SocketIO, emit
# from flask import Flask, session, render_template, request, jsonify
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


channels = {"main": [['Alfa', 'Betta'], [['13:18:08', 'Alfa', 'I always be first. Muhahaha'], ['13:18:10', 'Betta', 'ok, dude']]]}
users = set()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username', None) is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    return render_template("index.html", channels=channels)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user id
    users.discard(session.get('username', ''))
    session.clear()

    if request.method == "POST":
        username = request.form.get('username').split()[0]
        if username and username not in users:
            session['username'] = username
            return redirect('/')
        else:
            return render_template("login.html", message="nickname is empty or busy")

    return render_template("login.html", message="")


@app.route("/create_room", methods=["POST"])
@login_required
def create_room():
    room = request.form.get('new_room').split()[0]
    if room and room not in channels:
        channels[room] = [[],[]]
        # return redirect(f'/{room}')
    return redirect('/')


@app.route("/rooms/<string:room>", methods=["GET", "POST"])
@login_required
def rooms(room):
    if room not in channels:
        return redirect('/')
    users, msgs = channels[room]
    return render_template("room.html", room=room, users=users, msgs = msgs[-100:])


@socketio.on("send_msg")
def send_msg(data):
    room = data['room']
    text_msg =  data['text_msg']
    user = session.get("username", 'ohh, fucking_cheater!')
    date = datetime.now().strftime('%H:%M:%S')
    row = (date, user, text_msg)
    channels[room][1].append(row)
    emit("new_row", {'row': row}, broadcast=True)

    s = f'{date} {user} {text_msg}'
    print('Received msg', s)



