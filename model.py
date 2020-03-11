"""Models and database functions for running project."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_json import MutableJson, NestedMutableJson
from datetime import datetime, timedelta
from copy import copy
import random
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
    """Type of workout- repetition time distance"""
    __tablename__ = "forms"

    form_code = db.Column(db.String(10), primary_key=True, nullable=False)
    form_name = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        """Show form_code information"""
        return f"<Workout Forms form_code={self.form_code} form_type={self.form_type}>"


class BaseWorkout(db.Model):
    """Workout details"""
    
    __tablename__ = "base_workouts"

    bw_id = db.Column(db.Integer, autoincrement=True, primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    form_code = db.Column(db.String(10), db.ForeignKey('forms.form_code'))
    title = db.Column(db.String(30), nullable=False) 
    mon = db.Column(db.Boolean, nullable=False)
    tue = db.Column(db.Boolean, nullable=False)
    wed = db.Column(db.Boolean, nullable=False)
    thu = db.Column(db.Boolean, nullable=False)
    fri = db.Column(db.Boolean, nullable=False)
    sat = db.Column(db.Boolean, nullable=False)
    sun = db.Column(db.Boolean, nullable=False)

    user = db.relationship("User", backref="base_workouts")
    form = db.relationship("WorkoutForm", backref="base_workouts")



    def __repr__(self):
        """show info about user"""
        return f"<BaseWorkout bw_id={self.bw_id} title={self.title}>"

    @classmethod
    def get_by_weekday(cls, user_id, weekday):
        """Query class for a users workouts with a certain day = to true"""
        filter_dict = {
            'user_id': user_id,
            weekday: True
        }

        return cls.query.filter_by(**filter_dict).all()


class Specifications(db.Model):
    """specific wo details"""

    __tablename__ = "specs"

    spec_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    bw_id = db.Column(db.Integer, db.ForeignKey('base_workouts.bw_id'))
    title = db.Column(db.String(30), nullable=False)
    warmup = db.Column(db.Integer, nullable=False)
    wc_units = db.Column(db.String(15), nullable=False)
    body = db.Column(db.Integer, nullable=False)
    units= db.Column(db.String(15), nullable=False)
    repeats = db.Column(db.Integer, nullable=False, default=1)
    cooldown = db.Column(db.Integer, nullable=False)

    base_workout = db.relationship("BaseWorkout", backref="specs")
    user = db.relationship("User", backref="specs")

    def __repr__(self):
        """show info about user"""
        return f"<Workout Specifications id={self.bw_id} type={self.title}>"


def generate_calendar_workout(base_workout, cal, start_date):
    """Generate a workout on a given day"""
    spec = random.choice(base_workout.specs)
    wo_details = {}
    wo_details['warmup'] = spec.warmup
    wo_details['wc_units'] = spec.wc_units
    wo_details['cooldown'] = spec.cooldown
    wo_details['body'] = spec.body
    wo_details['units'] = spec.units
    wo_details['repeats'] = spec.repeats
    title = spec.title

    base_workout.workouts.append(Workout(spec_id=spec.spec_id, title=title, 
        user_id=base_workout.user_id, calendar_id=cal.calendar_id, 
        layout=wo_details,
        start_time=start_date,
        end_time=start_date
        ))
    db.session.commit()



class Workout(db.Model):
    """Scheduled workouts"""

    __tablename__ = "workouts"

    workout_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    bw_id = db.Column(db.Integer, db.ForeignKey('base_workouts.bw_id'))
    spec_id = db.Column(db.Integer, db.ForeignKey('specs.spec_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.calendar_id'))
    # json dictionary of wo frame + frame values
    layout = db.Column(MutableJson, nullable=False)  # make this JSON column type
    """{ 
        warmup: time
        wc_units: mi,km,min
        body: time | distance
        units: mi,km,m, min
        repeats: n times
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
    spec = db.relationship("Specifications", 
                                backref=db.backref("workouts", 
                                               order_by=start_time))

    def __repr__(self):
        """show info about user"""
        return f"<Workout workout_id={self.workout_id} title={self.title}>"
    

class CompletedWorkout(db.Model):
    """Result values corresponding to workout layout"""

    __tablename__ = "results"

    result_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.workout_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    spec_id = db.Column(db.Integer, db.ForeignKey('specs.spec_id'))
    # json of layout frame keys and result values

    result_values = db.Column(NestedMutableJson, nullable=True)  # rename this to something more related to results
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())


    workout = db.relationship("Workout", backref="result")
    spec = db.relationship("Specifications", backref="results")

    user = db.relationship("User",
                               backref=db.backref("results",
                                                  order_by=created_at))
    # move this relationship to Workout class
    # calendar = db.relationship("Calendar", secondary="workouts"
    #                            backref=db.backref("results",
    #                                               order_by=created_at))
    

    def __repr__(self):
        """show info about completed workout"""
        return f"<CompletedWorkout result_id={self.result_id} scheduled={self.title} entered={self.created_at}>"


class Calendar(db.Model):
    """Calendars to schedule workouts in"""

    __tablename__ = "calendars"

    calendar_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(50), nullable = False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    user = db.relationship("User",
                           backref=db.backref("calendars",
                                              order_by=title)) 

    def create_cal_wo_dict(self):
        """Gather details of calendars workouts"""

        wo_dict_list = []

        for workout in self.workouts:
            wo_dict_list.append({
                'id': workout.workout_id,
                'title': workout.title,
                'start': workout.start_time.isoformat(),
                'wolayout': workout.layout
                })
        return wo_dict_list

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Calendar id={self.title} 
                   user_id={self.user_id}>"""






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




