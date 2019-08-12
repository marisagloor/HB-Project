"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64))
    # password = db.Column(db.String(64), nullable=True)
    mile_count = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(15), nullable=False)

    def __repr__(self):
            """show info about user"""

            return f"<User user_id={self.user_id} email={self.email}>"


# Put your Movie and Rating model classes here.

class BaseWorkout(db.Model):

    __tablename__ = "base_workouts"

    cat_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable=False)
    # json dictionary days of the week + True False
    scheduling_rest = db.Column(db.String(77), nullable=False)
    repetition = db.Column(db.Boolean, nullable=False)
    t_restriction = db.Column(db.Boolean, nullable=False)
    d_restriction = db.Column(db.Boolean, nullable=False)


class Workout(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "workouts"

    workout_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('base_workouts.cat_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # json dictionary of wo frame + frame values
    layout = db.Column(db.String, nullable=False)
    occurence = db.Column(db.DateTime, nullable=False)
    completion = db.Column(db.Boolean, nullable=True)


    user = db.relationship("User",
                               backref=db.backref("ratings",
                                                  order_by=rating_id))
    movie = db.relationship("Movie",
                               backref=db.backref("ratings",
                                                  order_by=rating_id))

    def __repr__(self):
            """Provide helpful representation when printed."""

            return f"""<Rating rating_id={self.rating_id} 
                       movie_id={self.movie_id} 
                       user_id={self.user_id} 
                       score={self.score}>"""


class CompletedWorkout(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "relsults"

    result_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.workout_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.calendar_id'))
    # json of layout frame keys and result values
    layout = db.Column(db.Integer, nullable=True)

    user = db.relationship("User",
                               backref=db.backref("ratings",
                                                  order_by=rating_id))
    movie = db.relationship("Movie",
                               backref=db.backref("ratings",
                                                  order_by=rating_id))

    def __repr__(self):
            """Provide helpful representation when printed."""

            return f"""<Rating rating_id={self.rating_id} 
                       movie_id={self.movie_id} 
                       user_id={self.user_id} 
                       score={self.score}>"""


class Calendar(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "calendars"

    calendar_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    # user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship("User",
                               backref=db.backref("ratings",
                                                  order_by=rating_id))
    movie = db.relationship("Movie",
                               backref=db.backref("ratings",
                                                  order_by=rating_id))

    def __repr__(self):
            """Provide helpful representation when printed."""

            return f"""<Rating rating_id={self.rating_id} 
                       movie_id={self.movie_id} 
                       user_id={self.user_id} 
                       score={self.score}>"""






##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")