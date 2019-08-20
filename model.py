"""Models and database functions for running project."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_json import MutableJson
from datetime import datetime
# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = "scrtscrt"

##############################################################################
# Model definitions

class User(db.Model):
    """User of running website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(64), nullable=True)
    mile_count = db.Column(db.Integer, nullable=True)
     
    def __repr__(self):
        """show info about user"""
        return f"<User user_id={self.user_id} name={self.name}>"


class WorkoutForm(db.Model):

    __tablename__ = "forms"

    form_code = db.Column(db.String(10), primary_key=True, nullable=False)
    form_name = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        """Show form_code information"""
        return f"<Workout Forms form_code={self.form_code} form_type={self.form_type}>"


class BaseWorkout(db.Model):

    __tablename__ = "base_workouts"

    bw_id = db.Column(db.Integer, autoincrement=True, primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    form_code = db.Column(db.String(10), db.ForeignKey('forms.form_code'))
    title = db.Column(db.String(30), nullable=False)
    mon = db.Column(db.String, nullable=False)
    tues = db.Column(db.String, nullable=False)
    wed = db.Column(db.String, nullable=False)
    thurs = db.Column(db.String, nullable=False)
    fri = db.Column(db.String, nullable=False)
    sat = db.Column(db.String, nullable=False)
    sun = db.Column(db.String, nullable=False)

    user = db.relationship("User", backref="base_workouts")
    form = db.relationship("WorkoutForm", backref="base_workouts")

    def __repr__(self):
        """show info about user"""
        return f"<BaseWorkout bw_id={self.bw_id} type={self.title}>"



class Workout(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "workouts"

    workout_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    bw_id = db.Column(db.Integer, db.ForeignKey('base_workouts.bw_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.calendar_id'))
    # json dictionary of wo frame + frame values
    layout = db.Column(MutableJson, nullable=False)  # make this JSON column type
    """{ 
        warmup: time
        component:  | distance
        repetition: n times
        cooldown|time

    }"""
    start_time = db.Column(db.DateTime, nullable=False)  
    end_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User",
                           backref=db.backref("workouts",
                                              order_by=start_time))
    # add db.relationship for BaseWorkout
    base = db.relationship("BaseWorkout", 
                            backref=db.backref("workouts", 
                                                order_by=start_time))

    calendar = db.relationship("Calendar",
                                backref=db.backref("workouts",
                                              order_by=start_time))

    def __repr__(self):
        """show info about user"""
        return f"<Workout workout_id={self.workout_id} name={self.name}>"
    

class CompletedWorkout(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "results"

    result_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.workout_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    # json of layout frame keys and result values

    result_values = db.Column(db.Integer, nullable=True)  # rename this to something more related to results
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())


    workout = db.relationship("Workout", backref="result")

    user = db.relationship("User",
                               backref=db.backref("results",
                                                  order_by=created_at))
    # move this relationship to Workout class
    # calendar = db.relationship("Calendar",
    #                            backref=db.backref("results",
    #                                               order_by=created_at))
    

    def __repr__(self):
        """show info about completed workout"""
        return f"<CompletedWorkout result_id={self.result_id} scheduled={workout.occurence} entered={self.enter_date}>"


class Calendar(db.Model):
    """Ratings of movies by users"""

    __tablename__ = "calendars"

    calendar_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable = False) # add calendar name column
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    user = db.relationship("User",
                           backref=db.backref("calendars",
                                              order_by=name)) 

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Calendar id={self.name} 
                   user_id={self.user_id} 
                   start_date={self.start_date}>"""






##############################################################################
# Helper functions


def connect_to_db(app, db_name):
    """Connect the database to our Flask app."""

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql:///{db_name}"
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = app
    db.init_app(app)
    db.create_all()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app, "runners")
    print("Connected to DB")




