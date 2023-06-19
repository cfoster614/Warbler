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

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

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
        
        # __repr__(self) should look like the expected variable 
        expected = f"<User #{u.id}: {u.username}, {u.email}>"
        actual = str(u)
        self.assertEqual(actual, expected)
        
    def test_follows(self):
        
        db.session.add_all([
            User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        ),
            User(
            email = "cat@test.com",
            username = "catTest",
            password = "HASHED_PASSWORD"
        )
        ])
        db.session.commit()
       
        u = User.query.filter_by(username = 'testuser').first()
        u2 = User.query.filter_by(username = 'catTest').first()
        u2.following.append(u)
        db.session.commit()
       
        #is_followed_by should detect if user1 in followed by user2
        #or is should show that user2 is not followed by user1
        self.assertTrue(u.is_followed_by(u2))
        self.assertFalse(u2.is_followed_by(u))
        
        #is_following should detect if user1 is following user2, vice versa
        self.assertTrue(u2.is_following(u))
        self.assertFalse(u.is_following(u2))
            
    def test_authenication(self):
        u = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url=User.image_url.default.arg,)
        self.assertEqual(u.username, "testuser")
        #Password should be hashed during User.signup
        self.assertNotEqual(u.password, "HASHED_PASSWORD")
       
        #Check authentication. 
        #Should successfully return valid user
        self.assertTrue(User.authenticate("testuser", "HASHED_PASSWORD"))
        #Should fail to return user with invalid password
        self.assertFalse(User.authenticate("testuser", "meow"))
        #Should fail to return user with invalid username
        self.assertFalse(User.authenticate("test", "HASHED_PASSWORD"))
            
        