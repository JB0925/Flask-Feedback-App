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
    pass