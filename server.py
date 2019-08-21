from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect, flash, session

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, BaseWorkout, Workout, CompletedWorkout, Calendar, WorkoutForm

from sqlalchemy.orm.exc import NoResultFound

import datetime

import random


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    if not 'login_status' in session:
        session['login_status'] = False

    return render_template('homepage.html')


@app.route('/register', methods=['GET'])
def register_form():

    return render_template('sign_up_form.html')


@app.route('/register', methods=['POST'])
def process_registration():

    name = request.form.get('name')
    password = request.form.get('password')

    user = User(name=name, password=password)
    # user.name = name
    # user.password = password

    # We need to add to the session or it won't ever be stored
    db.session.add(user)
    # Once we're done, we should commit our work
    db.session.commit()
    session['login_status'] = True
    session['user_id'] = user.user_id

    # TODO: add conditions to html to change homepage when 
    # logged in - links for workouts, calendars etc
    return redirect('/')


@app.route('/add_workout_type', methods=['GET'])
def base_wo_form():

    return render_template('add_workout_type_form.html')


@app.route('/add_workout_type', methods=['POST'])
def add_base_wo():
    """Create base workout without specific workouts"""
    title = request.form.get('title')
    form = request.form.get('form')
    wucd = request.form.get('wu_cd')
    layout = {'warmup' : wucd, 
                'component': [],
                'cooldown': wucd
                }
    str_days = [request.form.get(f'day{i}') for i in range(1, 8)]
    days = []

    for day in str_days:
        if day == "True":
            days.append(True)
        else:
            days.append(False)

    user = User.query.get(session['user_id'])
    
    user.base_workouts.append(BaseWorkout(title=title, form_code=form, 
                                layout_choices=layout, mon=days[0], 
                                tues=days[1], wed=days[2],
                                thurs=days[3], fri=days[4], 
                                sat=days[5], sun=days[6]))
    db.session.commit()

    return redirect('/')


@app.route('/categories')
def workout_types():
    """Show all user's base_workouts"""

    base_workouts = BaseWorkout.query.filter_by(user_id=session['user_id']).all()
    return render_template('workout_categories.html', base_workouts=base_workouts)

# @app.route('/categories/<base_wo.bw_id>')
# def view_base_wo(base_id):
#     """show base workout details and add specific workout descriptions"""

#     return render_template(base_wo=BaseWorkout.query.get(base_id))

@app.route('/add_calendar', methods=['GET'])
def calendar_form():
    """Render the calendar creation form"""

    return render_template('create_calendar_form.html',
                            user=User.query.get(session['user_id']))


@app.route('/add_calendar', methods=['POST'])
def create_calendar():
    """Instantiate calendar"""
    title = request.form.get('title')
    cal = Calendar(user_id=session['user_id'], name=title)
    db.session.add(cal)
    db.session.commit()
    

    start_date = request.form.get('schedule-start')
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = request.form.get('schedule-end')
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    type(end_date)
    day_range = (end_date - start_date).days + 1
    print("\n\n\n", title, start_date, end_date, day_range, "\n\n\n\n")


    for n in range(day_range):
        print(n,
        datetime.date.isoweekday(start_date + datetime.timedelta(n)))
        weekday = datetime.date.isoweekday(start_date + datetime.timedelta(n))
        # IDEA TODO - change model.py tohave columnnames 'mon' etc AS 1
        curr_start = start_date + datetime.timedelta(n)
        weekday_str = datetime.datetime.strftime(curr_start, '%a').lower()

        base_workout = get_by_weekday(session['user_id'], weekday_str)
        if base_workout:
            base_workout.generate_calendar_workout(base_workout,
                                                     cal, start_date, n)

        

    return redirect('/')



@app.route('/login')
def login_form():

    return render_template('login_page.html')


@app.route('/check_login', methods=['GET'])
def check_login():
    name = request.args.get('name')
    password = request.args.get('password')

    try:
        user = User.query.filter(User.name == name).one()
        # user = User.query.get(user_id)

        if user.password == password:
        #flash message about success
            session['user_id'] = user.user_id
            session['login_status'] = True
            flash("Login Successful")
            # return redirect(f"/users/{user.user_id}")
            return redirect('/')
        else:
            flash("Login Failed, invalid email or PASSWORD")
            return redirect('/login')
    except NoResultFound:
        flash("Login Failed, invalid EMAIL or password")
        return redirect('/login')


@app.route('/logout')
def logout():

    del session['user_id']
    session['login_status'] = False

    return redirect('/')


# @app.route('/users/<int:user_id>')
# def user_detail(user_id):

#     user = User.query.get(user_id)

#     return render_template('user_details.html',
#                            user=user)

        


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app, "runners")

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')


    