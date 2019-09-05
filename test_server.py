from server import app
import unittest
import model


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask routes."""

 def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'

        
        # Connect to test database
        connect_to_db(app, "test")

        # Create tables and add sample data
        db.create_all()
        example_data()


    def test_home(self):
        """Make sure home page returns correct HTML """

        # Use the test client to make requests
        result = self.client.get('/')

        # Compare result.data with assert method
        if session['login_status'] == false:
            self.assertIn(b'<h1>Sign up</h1>', result.data)
        else:
            self.assertIn(b'<p><a href="/categories"> View Workout Categories</a><p>', result.data)


    def test_register(self):
        """Make sure register routes return correct HTML when not logged in."""

        # Use the test client to make requests
        get_result = self.client.get('/register')
        post_result = self.client.post('/register', data={'name': 'Austin', 'password':'jeep'})

        # Compare result.data with assert method
        self.assertIn(b'<h1>Sign-up Form</h1>', get_result.data)
        self.assertIn(b'<p><a href="/categories"> View Workout Categories</a><p>', post_result.data)

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                

    def test_add_workout_category(self):
        """Check that add_workout_category returns correct information"""


        post_result = self.client.post('/add_workout_category', data={'title': 'Runs', 'form': 'REP', 
                                        'day1': 'True', 'day2': 'False', 'day3': 'True', 
                                        'day4': 'False', 'day5': 'False', 'day6': 'False','day7': 'False'})

        self.assertIn(f"{b}'<h1>{ data.title }</h1>'", post_result.data)




class FlaskTestsLoggedIn(TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

    def test_important_page(self):
        """Test important page."""

        result = self.client.get("/important")
        self.assertIn(b"You are a valued user", result.data)




    
    if __name__ == "__main__":
        from server import app
        unittest.main()

        # test = TestFlaskRoutes()
        # test.test_home()
        # test.test_register()
        # test.test_add_workout_category()





        