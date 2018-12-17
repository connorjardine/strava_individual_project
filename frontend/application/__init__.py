from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
from flask_pymongo import PyMongo
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from stravalib import Client

from frontend.application.convert_gpx import *
from frontend.application.db import *
from frontend.application.stravauth import *
from frontend.application.athlete import *
from frontend.application.authorise import *
from frontend.application.gpx_comparison import *
from frontend.application.pickle import *
from frontend.application.map import *

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



    # Create tables, currently just users but will add more if necessary in the future.
    create_table()

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
                return redirect(url_for('profile'))

        return render_template('login.html', form=form)

    # Authentication page for connecting to Strava
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if get_headers() is not None:
            session['code'] = get_headers()

        form = RegisterForm()

        if form.validate_on_submit():
            code = session['code']
            username = form.username.data
            password = hash_md5(form.password.data)

            session['username'] = username
            session.permanent = True

            user = mongo.db.users
            user.insert({'code': code, 'username': username, 'password': password})
            return redirect(url_for('profile'))

        return render_template('register.html', form=form)

    @app.route('/logout')
    def logout():
        if 'username' not in session:
            session.pop('username')
        if 'code' not in session:
            session.pop('code')
        if 'location' not in session:
            session.pop('location')
        return redirect(url_for('preauth'))

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        username = session['username']
        code = session['code']
        form = RouteForm()

        send_url = "http://api.ipstack.com/check?access_key=6566a9efb41388f6d76eb0818815865f"
        geo_req = requests.get(send_url)
        geo_json = json.loads(geo_req.text)
        latitude = geo_json['latitude']
        longitude = geo_json['longitude']

        session['location'] = [latitude, longitude]

        if form.validate_on_submit():
            session['time'] = form.time.data
            session['distance'] = form.distance.data
            return redirect(url_for('routeview'))

        return render_template('profile.html', username=username, code=code, form=form)

    @app.route('/map')
    def mapview():
        # creating a map in the view
        trace = []
        runs = mongo.db.runs.find()
        for i in runs:
            trace += [thaw(i['trace']).name[0]]

        locations = convert_gpx(trace)
        mymap = Map(
            identifier="view-side",
            lat=locations[0]['lat'],
            lng=locations[0]['lon'],
            markers=[(loc['lat'], loc['lon'])
                     for loc in locations],
            fit_markers_to_bounds=True,
            style="height:500px;width:800px;margin:0;"
        )
        return render_template('map.html', mymap=mymap)

    @app.route('/routes')
    def routeview():
        # creating a map in the view
        trace = []
        data = []
        if session['time'] and session['distance']:
            routes = return_valid_routes(session['location'], 4500)
            for i in routes:
                trace += i[2]
                data += [[i[0], i[1]]]
        else:
            runs = mongo.db.runs.find()
            for i in runs:
                trace += [thaw(i['trace']).name[0]]

        locations = convert_gpx(trace)
        mymap = Map(
            identifier="view-side",
            lat=locations[0]['lat'],
            lng=locations[0]['lon'],
            markers=[(loc['lat'], loc['lon'])
                     for loc in locations],
            fit_markers_to_bounds=True,
            style="height:500px;width:800px;margin:0;"
        )
        return render_template('routeview.html', mymap=mymap, data=data)

    return app
