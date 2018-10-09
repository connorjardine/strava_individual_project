from flask import Flask, render_template

from frontend.application.db import *
from frontend.application.stravauth import *
from frontend.application.athlete import *


def create_app():
    # create and configure the app
    app = Flask(__name__)

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

    @app.route('/login')
    def login():
        return render_template('login.html')

    # Authentication page for connecting to Strava
    @app.route('/register')
    def register():

        return render_template('register.html',
                               auth=strava_auth(),
                               headers=get_headers())

    # Home page of the app
    @app.route('/athlete')
    def athlete():
        return render_template('athlete.html', get_users=get_users(), get_athlete=get_athlete_info())

    return app
