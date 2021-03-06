from flask import Flask, redirect, session, request, url_for, render_template
from decouple import config

from models import db, connect_db, User, Feedback


app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)
db.create_all()


@app.route('/home')
def home():
    """Renders a nice home page."""
    return render_template('home.html')


@app.route('/')
def redirect_to_register():
    """Root route that redirects to the register page."""
    return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page that allows a new user to sign up for
       an account."""
    if request.method == 'GET':
        if "username" in session:
            return redirect(url_for('secret', username=session["username"]))
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
    """The page that returns a user's profile."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('home'))

    if "username" in session and session["username"] == username:
        return render_template('secret.html', user=user, feedback=user.feedback)
    return redirect(url_for("register"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Allows a user to login to their account. If
       they are already logged in, it will redirect to their user
       profile."""
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
    """A method that does not render a template, but 
       pops the username from the session. and redirects
       to the register page."""
    try:
        session.pop("username")
    except KeyError:
        pass
    return redirect(url_for('register'))


@app.route('/users/<username>/delete')
def delete_user(username):
    """Deletes a user's profile from the database, 
       if the user exists and is logged in."""
    if "username" not in session:
        return redirect(url_for('home'))
    
    user = User.query.filter_by(username=username).first()
    if user and session['username'] == username:
        session.pop("username")
        db.session.delete(user)
        db.session.commit()
    session.pop("username")
    return redirect(url_for('register'))


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """Allows a logged in user to add feedback about the app."""
    if "username" not in session:
        return redirect(url_for('home'))

    if request.method == "GET":
        return render_template('add_feedback.html')
    
    if username == session["username"]:
        title = request.form['title']
        content = request.form['content']
        user = User.query.filter_by(username=username).first()
        if user:
            new_feedback = Feedback(title=title, content=content, username=username)
            db.session.add(new_feedback)
            db.session.commit()
    return redirect(url_for('secret', username=username))
    

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Allows a logged in user to update the feedback, if they are
       the one who created the feedback."""
    if "username" not in session:
        return redirect(url_for('home'))

    if request.method == "GET":
        return render_template('update_feedback.html')
    
    feedback = Feedback.query.get(feedback_id)
    if session["username"] == feedback.username:
        feedback.title = request.form.get("title", feedback.title)
        feedback.content = request.form.get("content", feedback.content)
        db.session.add(feedback)
        db.session.commit()
        return redirect(url_for('secret', username=feedback.username))
    return redirect(url_for('home'))


@app.route('/feedback/<feedback_id>/delete')
def delete_feedback(feedback_id):
    """Allows a user to delete feedback, if they
       are the one who created the feedback."""
    if "username" not in session:
        return redirect(url_for('home'))
    
    feedback = Feedback.query.get(feedback_id)
    if session["username"] == feedback.username:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(url_for('secret', username=session["username"]))
    return redirect(url_for('home'))