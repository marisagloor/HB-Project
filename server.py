from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect, flash, session, jsonify

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, BaseWorkout, Workout, CompletedWorkout, Calendar, WorkoutForm, generate_calendar_workout, Specifications

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
    """Takes user to the signup form"""

    return render_template('sign_up_form.html')


@app.route('/register', methods=['POST'])
def process_registration():
    """Adds user to the db from the signup form"""

    name = request.form.get('name')
    password = request.form.get('password')

    # User objects have a name password and user_id -> this auto increments
    user = User(name=name, password=password)

    db.session.add(user)
    db.session.commit()
    session['login_status'] = True
    #HTML displays information conditionally based on this cookie
    # logged in - links for workouts, calendars etc

    session['user_id'] = user.user_id
    # user_id is necessary in many of the following view functions,
    # until the user logs-out' this cookie can be accessed

    return redirect('/')


@app.route('/add_workout_category', methods=['GET'])
def base_wo_form():
    """Takes user to the form to add a general base_workout information"""

    return render_template('add_workout_type_form.html')


@app.route('/add_workout_category', methods=['POST'])
def add_base_wo():
    """Create base workout without specific workouts"""

    title = request.form.get('title')
    form = request.form.get('form')

    str_days = [request.form.get(f'day{i}') for i in range(1, 8)]
    # retrieve html input for each day-> these are strings
    days = []
    # change input into boolean for each day
    for day in str_days:
        if day == "True":
            days.append(True)
        else:
            days.append(False)

    user = User.query.get(session['user_id'])
    # get logged in user from user_id cookie
    # possible TODO - change 'user_id' cookie to a 'user' object cookie

    # Instantiate users base workout
    base_wo = BaseWorkout(title=title, form_code=form, mon=days[0], 
                                tue=days[1], wed=days[2],
                                thu=days[3], fri=days[4], 
                                sat=days[5], sun=days[6])
    user.base_workouts.append(base_wo)
    db.session.commit()

    # display base workouts details - this page has a form to add a specific wo to the category
    return render_template('category_details.html', base_wo=base_wo)


@app.route('/categories')
def workout_types():
    """Show all of user's base_workouts"""

    base_workouts = BaseWorkout.query.filter_by(user_id=session['user_id']).all()

    return render_template('workout_categories.html', base_workouts=base_workouts)


@app.route('/categories/<int:base_id>')
def view_base_wo(base_id):
    """show base workout details and show/add specific workout descriptions"""

    return render_template('category_details.html',
                            base_wo=BaseWorkout.query.get(base_id))


@app.route('/add_workout_specs/<int:base_id>', methods=['POST'])
def add_bwo_layout_choices(base_id):
    """Add a specific workout to a base workout's layout choices"""

    base_wo = BaseWorkout.query.get(base_id)
    title = request.form.get('title')
    body = int(request.form.get('body'))
    units = request.form.get('units')
    repeats = int(request.form.get('repeats'))
    wucd = int(request.form.get('wu_cd'))
    wc_units = request.form.get('wc_units')

    base_wo.specs.append(Specifications(user_id=session['user_id'], title=title, body=body, units=units,
                                     repeats=repeats, warmup=wucd, cooldown=wucd, wc_units=wc_units))

    db.session.commit()
    # adds nested mutable dictionary within components list in layout_choices dictionary

    return render_template('category_details.html',
                            base_wo=base_wo)


@app.route('/add_calendar', methods=['GET'])
def calendar_form():
    """Render the calendar creation form"""

    # pass in user with the potential of giving the user the option of 
    # specifying which base_workouts to use in their calendar schedule - currently not an option
    return render_template('create_calendar_form.html',
                            user=User.query.get(session['user_id']))


@app.route('/add_calendar', methods=['POST'])
def create_calendar():
    """Instantiate calendar and generate associated workout instances"""

    title = request.form.get('title')
    cal = Calendar(user_id=session['user_id'], title=title)
    db.session.add(cal)
    db.session.commit()
    # instantiated calendar does not have columns for start-end dates ->
    # a workout w/ datetime values is generated for each day in the user specified ran

    start_date = request.form.get('schedule-start')
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = request.form.get('schedule-end')
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    day_range = (end_date - start_date).days + 1


    for n in range(day_range):
        # gets day n days from the start date
        curr_start = start_date + datetime.timedelta(n)
        # gets the day of the week of the current start as 'mon', 'tue' etc ->
        # these match the column names for base_workout
        weekday_str = datetime.datetime.strftime(curr_start, '%a').lower()

        base_workouts = BaseWorkout.get_by_weekday(session['user_id'], weekday_str)
        # gets all base workouts for a user where the day of the week is true

        # chooses one baseworkout to generate a workout from
        if base_workouts:
            base_workout = random.choice(base_workouts)
            generate_calendar_workout(base_workout, cal, curr_start)

    return redirect('/')


@app.route('/calendars')
def view_calendars():
    """Show all of user's calendar"""

    calendars = Calendar.query.filter_by(user_id=session['user_id']).all()

    return render_template('calendars.html',
                            calendars=calendars,)


@app.route('/calendars/<int:cal_id>')
def view_cal(cal_id):
    """show base workout details and show/add specific workout descriptions"""

    cal = Calendar.query.get(cal_id)
    workouts = cal.workouts
    wo_dict_list = []
    for workout in workouts:
        wo_dict_list.append({
            'id': workout.workout_id,
            'title': workout.title,
            'start': workout.start_time.isoformat(),
            'wolayout': workout.layout
            })

    return render_template('calendar_details.html',
                            cal=cal,
                            workouts=wo_dict_list)


@app.route('/workout_event.json')
def get_workout():
    """Jsonify workout row for use in Javascript"""
    workout_id = request.args.get('id')
    workout = Workout.query.get(workout_id)

    WO_dets={'title':workout.title,
            'id': workout.workout_id,
                    'layout': workout.layout,
                    'start_time': workout.start_time,
                    'end_time' : workout.end_time}

    return jsonify(WO_dets)


@app.route('/enter_wo_results/<int:wo_id>', methods=['POST'])
def enter_results(wo_id):
    """Enter input from form into database"""
    workout = Workout.query.get(wo_id)
    if workout.layout['wc_units'] == "min":
        warmup = request.form.get('wu')
        cooldown = request.form.get('cd')
        wc_units = request.form.get('wc_result_units')

    else:
        warmup = int(request.form.get('min-wu-result'))
        print(warmup)
        wusec = int(request.form.get('sec-wu-result'))
        warmup = 60 * warmup
        warmup += wusec
        cooldown = int(request.form.get('min-cd-result'))
        cdsec = int(request.form.get('sec-cd-result'))
        cooldown *= 60 * warmup
        cooldown += cdsec
        wc_units = request.form.get('wc_result_units')
    if workout.layout["units"] == "min":
        reps = [request.form.get(f'body-result{rep}') for rep in range(workout.layout['repeats'])]
    else:
        reps = []
        for rep in range(workout.layout['repeats']):
            mins = request.form.get(f'min-body-result{rep}')
            print("mins:", mins)
            secs = request.form.get(f'sec-body-result{rep}')
            print("secs:", secs)
            time = (mins * 60) + secs
            reps.append(time)
    results = {'warmup': warmup, 'cooldown': cooldown, 'wc_units': wc_units, 'body': workout.layout['body'], 'results': reps}

    result = workout.result.append(CompletedWorkout(result_values=results, 
                            user_id=session['user_id'], title=workout.title, 
                            spec_id=workout.spec_id))
    db.session.commit()

    return redirect(f'/calendars/{workout.calendar_id}')


@app.route('/repeated_workouts.json')
def get_chartable_wo():
    """Gets users specific workouts that have multiple results"""
    user = User.query.get(session['user_id'])
    for spec in user.specs:
        if len(spec.results) > 1:
            return jsonify(get_result_data(spec.spec_id))


@app.route('/results.json/<int:spec_id>')
def get_result_data(spec_id):
    """Return data about results."""
    spec = Specifications.query.get(spec_id)
    # BAD RUNTIME - OPTIMIZE
    for result in spec.results:
        data_dict['labels'].append(f"{result.created_at}")
        data_dict['data'].append(result.result_values['results'][0])

    data_dict = {
                "labels": [],
                "datasets": [   { "data": [],
                    "backgroundColor": ["#FF6384",
                            "#36A2EB",],
                    "hoverBackgroundColor": ["#FF6384",
                            "#36A2EB",] }     ]
            }

    return data_dict


@app.route('/login')
def login_form():
    """Shows login page"""
    return render_template('login_page.html')


@app.route('/check_login', methods=['GET'])
def check_login():
    """Checks for login attempt in users and logs info in session"""
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
    """Removes login info from session"""

    del session['user_id']
    session['login_status'] = False

    return redirect('/')
        



# TODO decorator to check login



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


    