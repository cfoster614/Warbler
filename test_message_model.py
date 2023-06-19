import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        
        
    def test_message_model(self):
        """Does basic model work?"""
        
        u = User.query.filter_by(username = 'testuser').first()
        msg = Message(
            text = "This is a test.",
            timestamp = Message.timestamp.default.arg,
            user_id = u.id
        )
        db.session.add(msg)
        db.session.commit()
        
        #User should have a new message
        self.assertEqual(len(u.messages), 1)
        
        #Test that the Message.user relationship works
        expected = f"<User #{u.id}: {u.username}, {u.email}>"
        actual = str(msg.user)
        self.assertEqual(actual, expected)
        
        
        
        