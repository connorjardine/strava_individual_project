from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length

from frontend.application.db import *
from frontend.application.stravauth import *
from frontend.application.athlete import *
from frontend.application.authorise import *


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "Connor"

    class LoginForm(FlaskForm):
        username = StringField('username', validators=[InputRequired("A username is required."), Length(min=4, max=15)])

        password = PasswordField('password',
                                 default="Password",
                                 validators=[InputRequired("Password is required."),
                                             Length(min=8, max=80,
                                                    message="Password must be 8 characters or greater.")])

    class RegisterForm(FlaskForm):
        username = StringField('username', validators=[InputRequired("A username is required."), Length(min=4, max=15)])

        password = PasswordField('password',
                                 default="Password",
                                 validators=[InputRequired("Password is required."),
                                             Length(min=8, max=80, message="Password must be 8 characters or greater.")])

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
            return str(authorise_login(form.username.data, form.password.data))

        return render_template('login.html', form=form)

    # Authentication page for connecting to Strava
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            return redirect(strava_auth())
        return render_template('register.html',
                               form=form,
                               headers=get_headers())

        # Home page of the app

    @app.route('/profile')
    def profile():
        return render_template('profile.html', get_athlete=get_athlete_info(34913826))

    @app.route('/athlete')
    def athlete():
        return render_template('athlete.html', get_users=get_users(), get_athlete=get_athlete_info(34913826))

        # Home page of the app

    @app.route('/activity')
    def activity():
        return render_template('activity.html', get_users=get_users(), get_athlete=get_athlete_activities(34913826))

    return app
