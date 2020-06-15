import os
from functools import wraps

from flask import Flask, session, render_template, request, redirect
from flask_socketio import SocketIO, emit
# from flask import Flask, session, render_template, request, jsonify
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

chanels = {"18+": []}

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
    return render_template("index.html", chanels=chanels)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user id
    session.clear()

    if request.method == "POST":
        username = request.form.get('username')
        if username:
            session['username'] = username
            return redirect('/')

    return render_template("login.html", message="")
