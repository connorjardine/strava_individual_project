from flask import Flask, render_template, request

from frontend.application.db import return_users
from frontend.application.stravauth import strava_auth, get_headers


def create_app():
    # create and configure the app
    app = Flask(__name__)

    # Home page of the app
    @app.route('/')
    def base():
        return render_template('base.html')

    # Authentication page for connecting to Strava
    @app.route('/authenticate', methods=['POST', 'GET'])
    def authenticate():

        return render_template('authenticate.html', access_token=get_headers(), users=return_users(), auth=strava_auth())

    return app
