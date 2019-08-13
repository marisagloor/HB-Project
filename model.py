"""Models and database functions for running project."""

from flask_sqlalchemy import SQLAlchemy
# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of running website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    mile_count = db.Column(db.Integer, nullable=True)
    
    # email = db.Column(db.String(64))
    # password = db.Column(db.String(64), nullable=True)



    def __repr__(self):
            """show info about user"""
            return f"<User user_id={self.user_id} name={self.name}>"


class BaseWorkout(db.Model):

    __tablename__ = "base_workouts"

    cat_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    title = db.Column(db.String, nullable=False)

    # scheduling_rest = db.Column(db.String(77), nullable=False)
    repetition = db.Column(db.Boolean, nullable=False)
    t_restriction = db.Column(db.Boolean, nullable=False)
    d_restriction = db.Column(db.Boolean, nullable=False)

    mon = db.Column(db.Boolean, nullable=False)
    tues = db.Column(db.Boolean, nullable=False)
    wed = db.Column(db.Boolean, nullable=False)
    thurs = db.Column(db.Boolean, nullable=False)
    fri = db.Column(db.Boolean, nullable=False)
    sat = db.Column(db.Boolean, nullable=False)
    sun = db.Column(db.Boolean, nullable=False)

    user = db.relationship("User", backref="base_workouts")

    def __repr__(self):
            """show info about user"""
            return f"<BaseWorkout cat_id={self.cat_id} type={self.title}>"


class Workout(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "workouts"

    workout_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('base_workouts.cat_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # json dictionary of wo frame + frame values
    layout = db.Column(db.String, nullable=False)
    """{ 
        warmup: Y/N time | distance
        component: time | distance
        repetition: n times
        time_restric: wo time
        dist_restric: wo distance
        cooldown: Y/N time | distance

    }"""
    occurence = db.Column(db.DateTime, nullable=False)
    completion = db.Column(db.Boolean, nullable=True)


    user = db.relationship("User",
                               backref=db.backref("ratings",
                                                  order_by=rating_id))
    calendar = db.relationship("Calendar",
                               backref=db.backref("workouts",
                                                  order_by=workout.occurence))

    def __repr__(self):
            """show info about user"""
            return f"<Workout workout_id={self.workout_id} name={self.name}>"
    

class CompletedWorkout(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "results"

    result_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.workout_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.calendar_id'))
    # json of layout frame keys and result values
    layout = db.Column(db.Integer, nullable=True)
    enter_date = db.Column(db.DateTime, nullable=False)


    workout = db.relationship("Workout", backref="result")

    user = db.relationship("User",
                               backref=db.backref("results",
                                                  order_by=workout.occurence))
    calendar = db.relationship("Calendar",
                               backref=db.backref("results",
                                                  order_by=workout.occurence))
    

    def __repr__(self):
    """show info about completed workout"""
    return f"<CompletedWorkout result_id={self.result_id} scheduled={workout.occurence} entered={self.enter_date}>"


class Calendar(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "calendars"

    calendar_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # json dict of workout instances- OR- list of workout instances
    workouts = db.Column(db.Integer, nullable=False)
    # NULLABLE???
    start_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User",
                               backref=db.backref("calencars",
                                                  order_by=start_date))

    def __repr__(self):
            """Provide helpful representation when printed."""

            return f"""<Calendar id={self.rating_id} 
                       user_id={self.user_id} 
                       start_date={self.start_date}>"""






##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///runners'
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

