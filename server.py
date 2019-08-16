from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect, flash, session

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, BaseWorkout, Workout, CompletedWorkout, Calendar, WorkoutForm

from sqlalchemy.orm.exc import NoResultFound


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
def ase_wo_form():

    return render_template('add_workout_type_form.html')


@app.route('/add_workout_type', methods=['POST'])
def add_base_wo_form():
    title = request.form.get('title')
    form = request.form.get('form')
    days = [request.form.get(f'day{i}') for i in range(1, 8)]
    print(title, form, days)

    user = User.query.get(session['user_id'])
    
    user.base_workouts.append(BaseWorkout(title=title, 
                                form_code=form, mon=days[0], 
                                tues=days[1], wed=days[2],
                                thurs=days[3], fri=days[4], 
                                sat=days[5], sun=days[6]))
    db.session.commit()

    return redirect('/')


@app.route('/workout_types')
def workout_types():
    """Show all user's base_workouts"""
    pass


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


    