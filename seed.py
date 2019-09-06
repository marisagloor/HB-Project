
"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, BaseWorkout, Workout, Calendar, WorkoutForm, CompletedWorkout, Specifications

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
    

    workout1 = BaseWorkout(user_id=1,
                  title="LONG REPS",
                  form_code="REP",
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


def load_specifications():

    spec1 = Specifications(user_id=1, bw_id=1, title="Mile repeats", body=1, units="mi", repeats=3, warmup=.5, cooldown=.5, wc_units="mi")
    spec2 = Specifications(user_id=1, bw_id=1, title="1k repeats", body=1, units="km", repeats=5, warmup=.1, cooldown=.1, wc_units="km")
    spec3 = Specifications(user_id=1, bw_id=1, title="8k repeats", body=8, units="km" ,repeats=2, warmup=1, cooldown=1, wc_units="mi")
    spec4 = Specifications(user_id=1, bw_id=1, title="10k repeats", body=10, units="km", repeats=2, warmup=1, cooldown=1, wc_units="mi")
    spec5 = Specifications(user_id=1, bw_id=1, title="5k repeats", body=5, units="km", repeats=3, warmup=10, cooldown=10, wc_units="min")
    spec6 = Specifications(user_id=1, bw_id=1, title="Long hill repeats", body=300, units="m", repeats=5, warmup=.5, cooldown=.5, wc_units="mi")

    spec7 = Specifications(user_id=1, bw_id=2, title="Long run", body=10, units="km", warmup=.5, cooldown=.5, wc_units="mi")

    spec8 = Specifications(user_id=2, bw_id=3, title="300m repeats", body=300, units="m", repeats=5, warmup=5, cooldown=5, wc_units="min")

    spec9 = Specifications(user_id=1, bw_id=2, title="Arcata forest trail", body=8, units="mi", warmup=.5, cooldown=.5, wc_units="mi")

    db.session.add(spec1)
    db.session.add(spec2)
    db.session.add(spec3)
    db.session.add(spec4)
    db.session.add(spec5)
    db.session.add(spec6)
    db.session.add(spec7)
    db.session.add(spec8)
    db.session.add(spec9)
    db.session.commit()

def load_calendar():
    """Load a calendar into database."""

    

    calendar = Calendar(title="Fall Season",
                    user_id=1)

    db.session.add(calendar)

    db.session.commit()

def load_workout():
    """Create one workout"""

    jdict = {"warmup":.5, "body":1, "units": "mi", "repeats":1, "cooldown":.5, "wc_units": "mi" }
    workout = Workout(title="Mile repeats", bw_id=1, user_id=1, spec_id=1, calendar_id=1, 
                        layout=jdict, start_time=datetime.date.today(), end_time=datetime.date.today())
    db.session.add(workout)
    db.session.commit()


def empty_all_tables():
    """Clears data"""
    Workout.query.delete()
    Specifications.query.delete()
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
        load_specifications()
        load_calendar()
        load_workout()
        # set_val_user_id()

