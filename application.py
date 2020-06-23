import os
from functools import wraps
from datetime import datetime

from flask import Flask, session, render_template, request, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
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

# Configure socketio. without 'cors' don't work sending and receiving messages
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

# Store all room chats, with users and 100 messages
channels = {"main": [{'Alfa', 'Betta'}, [['13:18:08', 'Alfa', 'I always be first. Muhahaha'], ['13:18:10', 'Betta', 'ok, dude...']]]}
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
            users.add(username)
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
    return redirect('/')


@app.route("/rooms/<string:room>", methods=["GET", "POST"])
@login_required
def rooms(room):
    if room not in channels:
        return redirect('/')
    users, msgs = channels[room]
    return render_template("room.html", room=room, users=users, msgs = msgs)


@socketio.on("send_msg")
def send_msg(data):
    # prepare new message
    room = data['room']
    text_msg =  data['text_msg']
    user = session.get("username", 'ohh, fucking_cheater!')
    date = datetime.now().strftime('%H:%M:%S')
    row = (date, user, text_msg)

    # Add new message to room chat. and split to last 100
    channels[room][1].append(row)
    channels[room][1] = channels[room][1][-100:]

    # send message all users in this room
    emit("new_row", {'row': row, 'room': room}, room=room)

    s = f'{date} {user} {text_msg}'
    print('Received msg', s)
    print('namespase', f'/{room}')
    print(channels)


@socketio.on('join')
def on_join(data):
    """Update users list in room"""
    user = session.get("username", 'ohh, fucking_cheater!')
    room = data['room']

    # add to socket.io room for broadcast messages
    join_room(room)

    # add to local store
    channels[room][0].add(user)
    users = sorted(channels[room][0])

    print(f'{user} connect to', room, users)
    emit("new_user", {'users': users}, room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit(username + ' has left the room.', room=room)