import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
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
        self.testuser.following.append(self.extra_user)
        db.session.commit()
        
    def test_follower_following_pages(self):
        #Can user see who other people are following/being followed by?
        with self.client as c:
            member = User.query.filter_by(username = "extra").first()
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            #User should be able to access another user's page
            resp = c.get(f"/users/{member.id}")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div id="warbler-hero" class="full-width">', html)
            
            #User should be able to see another user's followers/who they are following
            resp = c.get(f"/users/{member.id}/following")
            self.assertEqual(resp.status_code, 200)
            resp = c.get(f"/users/{member.id}/followers")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser, member.followers)
            
            
    def test_logged_out_prohibition(self):
        #Can someone not logged in see member's followers/who they are following?    
        extra_user = User.query.filter_by(username = "extra").first()
        resp = self.client.get(f"/users/{extra_user.id}/following")
        self.assertEqual(resp.status_code, 302)
        
        resp = self.client.get(f"/users/{extra_user.id}/followers")
        self.assertEqual(resp.status_code, 302)
    
    def test_following_a_user(self):
        #Can logged in user follow/unfollow someone?
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            extra_user = User.query.filter_by(username = "extra").first()
            resp = c.post(f"users/follow/{extra_user.id}")
            self.assertEqual(resp.status_code, 302)
            #Member should be added to user's following list
            self.assertIn(extra_user, self.testuser.following)
            
            resp = c.post(f"users/stop-following/{extra_user.id}")
            self.assertEqual(resp.status_code, 302)
            #Member should be gone from user's following list
            self.assertNotIn(extra_user, self.testuser.following)
            
            resp = c.get(f"users/{self.testuser.id}/followers")
            self.assertEqual(resp.status_code, 200)
            
    def test_user_profile(self):
        #Can current user update their profile?
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            user = User.query.filter_by(username="testuser").first()
            
            #User should see edit profile form
            resp = c.get("/users/profile")
            self.assertEqual(resp.status_code, 200)
            
            #Update profile, redirect. Need to include password
            resp = c.post("/users/profile", data={"bio" : "Testing is great.", "password" : "testuser"})
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(user.bio, "Testing is great.")
            
    def test_deleteing_user(self):
        #Can current user delete their profile?
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post("/users/delete")
            users = User.query.all()
            #Redirect to homepage, should be signed out
            self.assertEqual(resp.status_code, 302)
            html = resp.get_data(as_text=True)
            self.assertNotIn('<li><a href="/logout">Log out</a></li>', html)
            #User should no longer be in the users database
            self.assertNotIn(self.testuser, users)
            
    
                
        
            
        
        
        