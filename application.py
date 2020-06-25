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
channels = {}
users = set()



def login_required(f):
    """ redirect to login page if user not log in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username', None)
        if username is None or username not in users:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    return render_template("index.html", channels=channels)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user info
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
        channels[room] = [{},[]]
    return redirect('/')


@app.route("/rooms/<string:room>", methods=["GET", "POST"])
@login_required
def rooms(room):
    if room not in channels:
        return redirect('/')
    msgs = channels[room][1]
    return render_template("room.html", room=room,  msgs=msgs)


@socketio.on("send_msg")
@login_required
def send_msg(data):
    """send new message to room or user"""
    room = data['room']
    text_msg =  data['text_msg'][-255:]
    user = session.get("username", 'ohh, fucking_cheater!')
    date = datetime.now().strftime('%H:%M:%S')
    row = (date, user, text_msg)

    # Broadcast message
    if data['for_user'] == '__All__':
        # Add new message to room chat. and split to last 100
        channels[room][1].append(row)
        channels[room][1] = channels[room][1][-100:]

        # send message all users in this room
        emit("new_row", {'row': row, 'pm': ''}, room=room)

    # For PM
    else:
        for_user = data['for_user']
        sid = channels[room][0].get(for_user, '')
        if sid:
            # to yourself
            emit("new_row", {'row': row, 'pm': for_user})
            # to opponent
            emit("new_row", {'row': row, 'pm': for_user}, room=sid)


@socketio.on('join')
def on_join(data):
    """Update users list in room"""
    user = session.get("username", 'ohh, fucking_cheater!')
    room = data['room']
    t = datetime.now().strftime('%H:%M:%S')

    # add to socket.io room for broadcast messages
    join_room(room)

    # add user to local room store
    channels[room][0][user] = request.sid
    users = sorted(channels[room][0])

    # system messsage. and updating  userslist for all users
    emit("new_user", {'users': users, 'user': user, 'time': t}, room=room)


@socketio.on('leave')
def on_leave(data):
    print('Try to leave ...')
    user = session.get("username", 'ohh, fucking_cheater!')
    room = data['room']
    t = datetime.now().strftime('%H:%M:%S')

    # leave socket.io 'room'
    leave_room(room)

    # delete user from local room store
    channels[room][0].pop(user, '')
    users = sorted(channels[room][0])

    # system messsage and updating userslist for all users
    emit("leave_user", {'users': users, 'user': user, 'time': t}, room=room)
