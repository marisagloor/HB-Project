
"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, BaseWorkout, Workout, Calendar, WorkoutForm, CompletedWorkout

from model import connect_to_db, db
from server import app
import datetime



def load_forms():
    """Load users from u.user into database."""

    print("Forms")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    

    # Read u.user file and insert data

    db.session.add(WorkoutForm(form_code="REP", form_name="repetition"))
    db.session.add(WorkoutForm(form_code="TIME", form_name="time"))
    db.session.add(WorkoutForm(form_code="DIS", form_name="distance"))
    db.session.commit()



def load_users():
    """Load users  into database."""

    print("Users")

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    

    # Read u.user file and insert data

    user = User(name="Marisa",
                password="GLOOR")

    user2 = User(name="Rina",
                password="NOEL")
        # We need to add to the session or it won't ever be stored
    db.session.add(user)
    db.session.add(user2)


    # Once we're done, we should commit our work
    db.session.commit()



def load_base_workouts():
    """Load sample workouts"""
    layout1 = {
              'warmup': 'time',
              'components': [{"title": "Mile repeats", "body": "1 mile", "repetition": 3},
                            {"title": "1k repeats", "body": "1000m", "repetition": 5}, 
                            {"title": "8k repeats", "body": "8000m", "repetition": 2}, 
                            {"title": "10k repeats", "body": "10,000m", "repetition": 2}, 
                            {"title": "5k repeats", "body": "5000m", "repetition": 3}, 
                            {"title": "Long hill repeats", "body": "300m", "repetition": 5}],
              'cooldown': 'time'
    }

    layout2 = {
              'warmup': 'time',
              'components': [{'title':'long run', 'body': '10k', "repetition": 1}],
              'cooldown': 'time'
    }
    layout3 = {
              'warmup': 'time',
              'components': [{'title':'300m repeats', 'body': '300m', "repetition": 5}],
              'cooldown': 'time'
    }
    layout4 = {
              'warmup': 'time',
              'components': [{'title':'Arcata forest trail', 'body': '1hr', "repetition": 1}],
              'cooldown': 'time'
    }
    

    workout1 = BaseWorkout(user_id=1,
                  title="LONG REPS",
                  form_code="REP",
                  layout_choices=layout1,
                  mon=False,
                  tue=False,
                  wed=True,
                  thu=False,
                  fri=False,
                  sat=False,
                  sun=False)
    workout2 = BaseWorkout(user_id=1,
                  title="LONG RUNS",
                  form_code="DIS",
                  layout_choices=layout2,
                  mon=True,
                  tue=False,
                  wed=False,
                  thu=False,
                  fri=False,
                  sat=False,
                  sun=False)
    workout3 = BaseWorkout(user_id=2,
                  title="TRACK RUNS",
                  form_code="REP",
                  layout_choices=layout3,
                  mon=False,
                  tue=False,
                  wed=True,
                  thu=False,
                  fri=True,
                  sat=False,
                  sun=False)
    workout4 = BaseWorkout(user_id=2,
                  title="TRAIL RUNS",
                  form_code="TIME",
                  layout_choices=layout4,
                  mon=True,
                  tue=False,
                  wed=True,
                  thu=True,
                  fri=False,
                  sat=False,
                  sun=False)


    db.session.add(workout1)
    db.session.add(workout2)
    db.session.add(workout3)
    db.session.add(workout4)

    db.session.commit()


def load_calendar():
    """Load a calendar into database."""

    

    calendar = Calendar(name="Fall Season",
                    user_id=2)

    db.session.add(calendar)

    db.session.commit()

def load_workout():
    """Create one workout"""


    jdict = {"WU":"time", "Component":"distance", "repeats":1, "CD":"time"}
    workout = Workout(name="100mreps", bw_id=3, user_id=2, calendar_id=1, 
                        layout=jdict, start_time=datetime.date.today(), end_time=datetime.date.today())
    db.session.add(workout)
    db.session.commit()


def empty_all_tables():
    """Clears data"""
    Workout.query.delete()
    Calendar.query.delete()
    BaseWorkout.query.delete()
    User.query.delete()
    WorkoutForm.query.delete()


# def set_val_user_id():
#     """Set value for the next user_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(User.user_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('users_user_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()


if __name__ == "__main__":
    connect_to_db(app, "runners")

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    if input("ARE YOU SURE Y/N?") == "Y":
        empty_all_tables()
        load_users()
        load_forms()
        load_base_workouts()
        # load_calendar()
        # load_workout()
        # set_val_user_id()

