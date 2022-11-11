"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        self.client = app.test_client()
    def tearDown(self):
        """delete models"""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test___repr__(self):
        """Does the repr method work as expected"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        p = u.__repr__()
        self.assertEqual(p, '<User #None: testuser, test@test.com>')

    def test_is_following(self):
        """Does is_following successfully detect when user1 is (not) following user2?"""
        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = u = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        # Does is_following successfully detect when user1 is following user2?
        self.assertEqual(u1.is_following(u2), False)
        u1.following.append(u2)
        db.session.commit()
        # Does is_following successfully detect when user1 is not following user2?
        self.assertEqual(u1.is_following(u2), True)
    
    def test_is_followed_by(self):
        """Does is_followed_by successfully detech when user1 is/not followed by user 2?"""
        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = u = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        # Does is_followed_by successfully detect when user1 is followed by user2?
        self.assertEqual(u1.is_followed_by(u2), False)
        u1.followers.append(u2)
        db.session.commit()
        # Does is_followed_by successfully detect when user1 is not followed by user2?
        self.assertEqual(u1.is_followed_by(u2), True)
    
    def test_signup(self):
        """# Does User.create successfully create a new user given credentials?"""
        u = User.signup(username='test123', email='email@test.com', password='password', image_url='http://www.abc.com/123.jpg')
        self.assertEqual(u.username, 'test123')     
        self.assertNotEqual(u.password, 'password')
        # Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
        try:
            bad_user = User.signup(username='test123', email='blah', password='blah')
        except:
            err = True;
        self.assertEqual(err, True)
    
    def test_authenticate(self):
        # Does User.authenticate successfully return a user when given a valid username and password?
        # Does User.authenticate fail to return a user when the username is invalid?
        # Does User.authenticate fail to return a user when the password is invalid?
        u = User.signup(username='test123', email='email@test.com', password='password', image_url='http://www.abc.com/123.jpg')
        self.assertEqual(u.authenticate('test123', 'password'), User.query.filter_by(username='test123').first())
        self.assertEqual(u.authenticate('test124', 'password'), False)
        self.assertEqual(u.authenticate('test123', 'pasword'), False)
