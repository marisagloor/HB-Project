import server
import unittest


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask routes."""

    def test_home(self):
        """Make sure home page returns correct HTML when not logged in."""

        # Create a test client
        client = server.app.test_client()

        # Use the test client to make requests
        result = client.get('/')

        # Compare result.data with assert method
        if session['login_status'] = false:
            self.assertIn(b'<h1>Sign up</h1>', result.data)
        else
            self.assertIn(b'<p><a href="/categories"> View Workout Categories</a><p>', result.data)


    def test_home(self):
        """Make sure register routes return correct HTML when not logged in."""

        # Create a test client
        client = server.app.test_client()

        # Use the test client to make requests
        get_result = client.get('/register')
        post_result = client.post('/register')

        # Compare result.data with assert method
        if session['login_status'] = false:
            self.assertIn(b'<h1>Sign up</h1>', result.data)
        else
            self.assertIn(b'<p><a href="/categories"> View Workout Categories</a><p>', result.data)