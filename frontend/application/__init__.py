from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm, widgets
from wtforms import PasswordField, IntegerField
from wtforms.validators import InputRequired, Length

from frontend.application.db import *
from frontend.application.stravauth import *
from frontend.application.athlete import *
from frontend.application.password_hash import *


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "Connor"

    class LoginForm(FlaskForm):
        athlete_id = IntegerField('athlete_id',
                                  validators=[InputRequired("An Athlete ID is required.")])

        password = PasswordField('password',
                                 default="Password",
                                 validators=[InputRequired("Password is required."),
                                             Length(min=8, message="Password must be 8 characters or greater.")])

    # Create tables, currently just users but will add more if necessary in the future.
    create_table()

    # Home page of the app
    @app.route('/')
    def base():
        return render_template('base.html')

    # Debug page for printing values. TEMPORARY.
    @app.route('/debug')
    def debug():
        return render_template('debug.html', get_users=get_users())

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            if get_user_by_athlete_id(form.athlete_id.data):
                hashed_password = hash_md5(form.password.data)
                if get_password(hashed_password):
                    return redirect(url_for('athlete'))
            else:
                return "Invalid Username or Password"

            render_template('athlete.html', get_users=get_users(), get_athlete=get_athlete_info(34913826))
        return render_template('login.html', form=form)

    # Authentication page for connecting to Strava
    @app.route('/register')
    def register():

        return render_template('register.html',
                               auth=strava_auth(),
                               headers=get_headers())

    # Home page of the app
    @app.route('/athlete')
    def athlete():
        return render_template('athlete.html', get_users=get_users(), get_athlete=get_athlete_info(34913826))

        # Home page of the app

    @app.route('/activity')
    def activity():
        return render_template('activity.html', get_users=get_users(), get_athlete=get_athlete_activities(34913826))

    return app
