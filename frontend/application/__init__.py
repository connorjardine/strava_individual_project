from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length
from flask_pymongo import PyMongo
from flask_googlemaps import GoogleMaps
from flask_bootstrap import Bootstrap
from stravalib import Client

from frontend.application.gpx_comparison import *
from frontend.application.services import *

import sys
import requests
import json


def create_app():
    # create and configure the app
    app = Flask(__name__)

    app.config['SECRET_KEY'] = "Connor"

    app.config['MONGO_DBNAME'] = 'connor'
    app.config['MONGO_CONNECT'] = False
    app.config["MONGO_URI"] = 'mongodb://connor:Password1@ds127094.mlab.com:27094/c_strava'
    mongo = PyMongo(app)

    app.config['GOOGLEMAPS_KEY'] = "AIzaSyCg3YkqcvCWvX0hYpWS_XEjT21a1HOmI0c"
    GoogleMaps(app)

    Bootstrap(app)

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

    class RouteForm(FlaskForm):
        distance = StringField('distance')
        time = StringField('time')
        elevation = IntegerField('elevation')
        latitude = FloatField('latitude')
        longitude = FloatField('longitude')



    # Authentication page for connecting to Strava
    @app.route('/', methods=['GET', 'POST'])
    def preauth():
        return render_template('preauth.html', auth=strava_auth())

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = hash_md5(form.password.data)

            users = mongo.db.users
            existing_user = users.find_one({'username': username, 'password': password})
            if existing_user is not None:
                session['username'] = username
                session['code'] = existing_user['code']
                session['profile'] = get_profile_info(existing_user['code'])
                return redirect(url_for('profile'))

        return render_template('login.html', form=form)

    # Authentication page for connecting to Strava
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if get_headers() is not None:
            session['code'] = get_headers()

        form = RegisterForm()

        if form.validate_on_submit():
            username = form.username.data
            password = hash_md5(form.password.data)

            users = mongo.db.users
            existing_user = users.find_one({'username': username, 'password': password})

            if existing_user is not None:
                code = session['code']
                session['profile'] = get_profile_info(code)
                session['username'] = username
                session.permanent = True

                users.insert({'code': code, 'username': username, 'password': password})
                return redirect(url_for('profile'))

        return render_template('register.html', form=form, auth=strava_auth())

    @app.route('/logout')
    def logout():
        if 'username' not in session:
            session.pop('username')
        if 'code' not in session:
            session.pop('code')
        if 'location' not in session:
            session.pop('location')
        if 'elevation' not in session:
            session.pop('elevation')
        return redirect(url_for('login'))

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        username = session['username']
        code = session['code']
        profile = session['profile']
        form = RouteForm()

        if form.validate_on_submit():
            session['location'] = [form.latitude.data, form.longitude.data]
            session['time'] = form.time.data
            session['distance'] = int(form.distance.data)
            session['elevation'] = form.elevation.data
            return redirect(url_for('routeview'))

        return render_template('profile.html', username=username, form=form, profile=profile)

    @app.route('/comparison', methods=['GET', 'POST'])
    def comparison():
        users = mongo.db.users.find()
        data = []
        for i in users:
            avg_pace = "{0:.2f}".format(float(thaw(i['pace']).name[0]) / float(thaw(i['pace']).name[1]))
            data += [[i['username'], avg_pace]]
        print(data, file=sys.stderr)
        return render_template('comparison.html', data=data)

    @app.route('/map')
    def mapview():
        runs = mongo.db.runs.find()
        map_coords = []
        j = 0
        for i in runs:
            map_coords += [[thaw(i['trace']).name[0], thaw(i['trace']).name[5][0][0], thaw(i['trace']).name[5][0][1]]]
            j += 1
            if j == 10:
                break
        return render_template('map.html', runs=map_coords)

    @app.route('/routes')
    def routeview():
        route_trace = []
        if session['time'] and session['distance'] and session['location'] and session['elevation']:
            route_trace = return_valid_routes(session['location'], session['distance'],
                                              session['time'], session['elevation'])
        else:
            return redirect(url_for('map'))
        return render_template('routeview.html', routes=route_trace)

    return app
