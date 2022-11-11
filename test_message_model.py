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
db.drop_all()
db.create_all()

u = User(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD"
        )
db.session.add(u)
db.session.commit()

class MessageModelTestCase(TestCase):
    """Test views for messages."""


    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        self.client = app.test_client()
        

    
    def test_new_message(self):
        """Does this create a new message object with valid data?"""
        user = User.query.filter_by(username='testuser').first()
        new_msg = Message(text='test message', user_id=u.id)
        self.assertEqual(new_msg.text, 'test message')
        db.session.add(new_msg)
        db.session.commit()
    def test_relationship(self): 
        """Does my relationship with users table work?"""
        msg = Message.query.filter_by(text='test message').first()
        self.assertEqual(msg.user.username, 'testuser')
    def test_null(self): 
        """Does my relationship with users table work?"""
        bad_msg = Message(text=None, user_id=u.id)
        try:
            db.session.add(bad_msg)
            db.session.commit()
        except:
            err = True
            db.session.rollback()    
        self.assertEqual(err, True)
    

   

