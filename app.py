import os
from time import localtime, strftime
from flask import Flask, render_template, redirect ,url_for, flash
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_manager, login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO, join_room, leave_room, rooms, send, emit
from wtf_forms import *
from models import *

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("POSTGRE_SQL") 
db=SQLAlchemy(app)

socketio= SocketIO(app)
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

ROOMS = ["General", "Network", "News", "Games", "Coding"]

@app.route("/",methods=["GET","POST"])
def index():
    
    reg_form = RegistrationForm() 
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        hashed_pass=pbkdf2_sha256.hash(password)

        user = User(username=username, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for("login"))

    return render_template("index.html",form= reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():

    login_form = LoginForm()

    # Allow login if validation success
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for("chat"))

    return render_template("login.html", form=login_form)

@app.route("/chat", methods=['GET', 'POST'])
def chat():

    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for("login"))

    return render_template("chat.html", username=current_user.username,rooms=ROOMS)

@app.route("/logout", methods=['GET'])
def logout():

    # Logout user
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for("login"))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@socketio.on('incoming-msg')
def on_message(data):
    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    time_stamp = strftime('%b-%d %I:%M%p', localtime())
    send({"username": username, "msg": msg, "time_stamp": time_stamp}, room=room)

@socketio.on('join')
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    send({"msg": username + " has joined the " + room + " room."}, room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send({"msg": username + " has left the room"}, room=room)

if __name__ == "__main__":

    app.run(debug=True)
