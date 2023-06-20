"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from flask import session
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.extra_user = User.signup(username = "extra",
                                      email="extra.com",
                                      password="test",
                                      image_url=None)
        db.session.commit()
        self.testpost = Message(text="Testing",
                                timestamp=Message.timestamp.default.arg,
                                user_id=self.extra_user.id)
        db.session.add(self.testpost)
        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter_by(text="Hello").one()
            self.assertEqual(msg.text, "Hello")
            
            get_resp = c.get("/messages/new")
            html = get_resp.get_data(as_text=True)
            
            #Should render message form
            self.assertEqual(get_resp.status_code, 200)
            self.assertIn('<button class="btn btn-outline-success btn-block">Add my message!</button>', html)
            
            delete = c.post(f"/messages/{msg.id}/delete")
            self.assertEqual(delete.status_code, 302)
            
            
    def test_messages(self):
        """Is user able to click into a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            msg = Message.query.filter_by(user_id = self.extra_user.id).first()
            get_resp = c.get(f"/messages/{msg.id}")
            html = get_resp.get_data(as_text=True)
            self.assertEqual(get_resp.status_code, 200)
            #Message from another user should not show the delete button
            self.assertNotIn('<button class="btn btn-outline-danger">Delete</button>', html)
            
            #User should not be able to delete a message not made by them
            delete = c.post(f"/messages/{msg.id}/delete")
            self.assertEqual(delete.status_code, 302)
            
            
            
    def test_auth_for_messages(self):
        #If user not logged in, shouldn't be able to create a new message
        resp = self.client.get(f"/messages/new")
        #Check redirect to homepage
        self.assertEqual(resp.status_code, 302)
        
        #If not logged in, shouldn't be able to delete a message
        resp = self.client.get(f"/messages")
        
        #Shouldn't be able to add a new message
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)
        self.assertNotIn('<li><a href="/messages/new">New Message</a></li>', html)
        
            
            
