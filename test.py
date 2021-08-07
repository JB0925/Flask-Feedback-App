from unittest import TestCase

from decouple import config
from flask_bcrypt import Bcrypt
import flask

from app import app
from models import db, User, Feedback

app.config["SQLALCHEMY_DATABASE_URI"] = config("TEST_DB")

db.drop_all()
db.create_all()

bcrypt = Bcrypt()

class FeedbackTestCase(TestCase):
    def setUp(self) -> None:
        User.query.delete()
        Feedback.query.delete()
    

    def tearDown(self) -> None:
        db.session.rollback()
    

    def login_user(self):
        with app.test_client() as client:
            return client.post('/login', data={"username": "kim08", "password": "cookies"},
                                follow_redirects=True)
    
    
    def logout_user(self):
        with app.test_client() as client:
            return client.get('/logout')
    

    def make_user(self):
        password = bcrypt.generate_password_hash('cookies').decode('utf-8')
        user = User(username='kim08', password=password, email='kim@gmail.com', 
                    first_name='kim', last_name='clark')
        db.session.add(user)
        db.session.commit()
        return user
    

    def remove_from_db(self, db_item):
        db.session.delete(db_item)
        db.session.commit()
    

    def make_feedback(self):
        feedback = Feedback(title="Flask is great!!!", content="Flask is so awesome! I love it!", username="kim08")
        db.session.add(feedback)
        db.session.commit()
        return feedback
    

    def test_home_route(self):
        with app.test_client() as client:
            resp = client.get('/home')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Flask Feedback', resp.get_data(as_text=True))
    

    def test_register_page(self):
        with app.test_client() as client:
            resp = client.get('/register')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign up for an account!', resp.get_data(as_text=True))

            data = {
                "username": "Joe007",
                "password": "blah",
                "email": "joe@gmail.com",
                "first_name": "Joe",
                "last_name": "Banks"
            }
            resp2 = client.post('/register', data=data, follow_redirects=True)
            users = len(User.query.all())
            self.assertEqual(resp2.status_code, 200)
            self.assertIn("Joe", resp2.get_data(as_text=True))
            self.assertEqual(1, users)
            joe = User.query.filter_by(username="Joe007").first()
            self.remove_from_db(joe)
    

    def test_login_and_users_page(self):
        with app.test_client() as client:
            user = self.make_user()
            resp = self.login_user()
            self.assertEqual(resp.status_code, 200)
            self.assertIn('kim', resp.get_data(as_text=True))
            self.remove_from_db(user)
    

    def test_logout(self):
        user = self.make_user()
        self.login_user()
        self.logout_user()
        with app.test_client() as client:
            resp = client.get(f'/users/{user.username}', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up for an account!", resp.get_data(as_text=True))
        self.remove_from_db(user)
    

    def test_delete_user(self):
        user = self.make_user()
        with app.test_client() as client:
            with client.session_transaction() as sesh:
                sesh["username"] = "kim08"
            
            resp = client.get('/logout')
            self.assertEqual(resp.status_code, 302)
            self.assertNotIn("username", flask.session)
    

    def test_add_feedback(self):
        with app.test_client() as client:
            with client.session_transaction() as sesh:
                sesh["username"] = "kim08"
            
            user = self.make_user()
            data = {"title": "hello", "content": "world"}
            resp = client.post(f'/users/{user.username}/feedback/add', data=data, follow_redirects=True)
            feedback = Feedback.query.filter_by(title="hello").first()
            self.assertEqual(resp.status_code, 200)
            self.assertIn("world", resp.get_data(as_text=True))
            self.assertEqual(1, len(Feedback.query.all()))
            self.remove_from_db(user)
            self.remove_from_db(feedback)
    

    def test_delete_feedback(self):
        with app.test_client() as client:
            with client.session_transaction() as sesh:
                sesh["username"] = "kim08"
            
            user = self.make_user()
            feedback = self.make_feedback()
            resp = client.get(f'/feedback/{feedback.id}/delete')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(0, len(Feedback.query.all()))
            self.remove_from_db(feedback)
            self.remove_from_db(user)
    

    def test_update_feedback(self):
        with app.test_client() as client:
            with client.session_transaction() as sesh:
                sesh["username"] = "kim08"
            
            user = self.make_user()
            feedback = self.make_feedback()
            data = {"title": "updated", "content": "info"}
            resp = client.post(f'/feedback/{feedback.id}/update', data=data)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual("updated", feedback.title)
            self.remove_from_db(user)
            self.remove_from_db(feedback)