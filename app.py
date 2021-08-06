from flask import Flask, redirect, session, request, url_for, render_template
from decouple import config

from models import db, connect_db, User


app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)
db.create_all()


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/')
def redirect_to_register():
    return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    username = request.form['username']
    password = request.form['password']
    email =  request.form['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    user = User.register(username, password, email, first_name, last_name)
    db.session.add(user)
    db.session.commit()
    session["username"] = username
    return redirect(url_for('secret', username=username))


@app.route('/users/<username>')
def secret(username):
    if "username" in session and session["username"] == username:
        user = User.query.filter_by(username=username).first()
        return render_template('secret.html', user=user)
    return redirect(url_for("register"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        if "username" in session:
            user = User.query.filter_by(username=session["username"]).first()
            return redirect(url_for('secret', username=user.username))
        return render_template('login.html')
    
    username = request.form['username']
    password = request.form['password']
    user = User.authenticate(username, password)
    if user:
        session["username"] = user.username
        return redirect(url_for('secret', username=user.username))
    return redirect(url_for('register'))


@app.route('/logout')
def logout():
    session.pop("username")
    return redirect(url_for('register'))