from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect, flash, session

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, BaseWorkout, Workout, CompletedWorkout, Calendar

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
def add_base_wo_form():

    return render_template('add_workout_type_form.html')

# @app.route('/login', methods=['GET'])
# def login_form():

#     return render_template('login_form.html')


# @app.route('/logged_in', methods=['GET'])
# def logged_in():
#     user_id = request.args.get('user_id')
#     password = request.args.get('password')

#     try:
#         # user = User.query.filter(User.email == email).one()
#         user = User.query.get(user_id)

#         if user.password == password:
#         #flash message about success
#             session['user_id'] = user.user_id
#             flash("Login Successful")
#             return redirect(f"/users/{user.user_id}")
#         else:
#             flash("Login Failed, invalid email or PASSWORD")
#             return redirect('/login')
#     except NoResultFound:
#         flash("Login Failed, invalid EMAIL or password")
#         return redirect('/login')


# @app.route('/logout')
# def logout():

#     del session['user_id']

#     return redirect('/')


# @app.route('/users/<int:user_id>')
# def user_detail(user_id):

#     user = User.query.get(user_id)

#     return render_template('user_details.html',
#                            user=user)


# @app.route('/add_workout_type>', methods=['POST'])
# def rate_movie():
#     user_id = session['user_id']
#     user = User.query.get(user_id)

#     return render_template('workout_types.html', user=user)
        


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


    