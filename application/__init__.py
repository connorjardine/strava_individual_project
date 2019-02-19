from __future__ import absolute_import
from flask import Flask, render_template, session, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap

from .func.gpx_comparison import *
from .data_pickle import *
from .func.services import *
from .func.handle_runs import *

import sys
from datetime import datetime


def create_app():
    # create and configure the app
    app = Flask(__name__)

    app.config['SECRET_KEY'] = "Connor"

    app.config['MONGO_DBNAME'] = 'connor'
    app.config['MONGO_CONNECT'] = False
    app.config["MONGO_URI"] = 'mongodb://connor:Password1@ds127094.mlab.com:27094/c_strava'
    app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'
    app.config['CELERY_RESULT_BACKEND'] = 'pyamqp://guest@localhost//'
    mongo = PyMongo(app)
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
        range = IntegerField('range')

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

                if existing_user['after'] is not "":
                    parse_runs.delay(session['code'], 10, after=thaw(existing_user['after']).name)
                else:
                    parse_runs.delay(session['code'], 10, after=freeze(datetime.now()))
                db.users.update_one({"_id": existing_user['_id']},
                                    {"$set": {"after": freeze(datetime.now()), "tasks": "RUNNING"}})
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

                users.insert({'code': code, 'username': username, 'password': password,
                              'after': datetime.now(), "tasks": "RUNNING"})
                parse_runs.delay(code, 10, after=None)
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
            session['range'] = form.range.data
            return redirect(url_for('routeview'))

        return render_template('profile.html', username=username, form=form, profile=profile)

    @app.route('/comparison', methods=['GET', 'POST'])
    def comparison():
        users = mongo.db.users.find()
        data = []
        for i in users:
            if i['pace'] is not "":
                print(i['pace'], file=sys.stderr)
                avg_pace = thaw(i['pace'])['name']
                print(avg_pace, file=sys.stderr)
                data += [[i['username'], avg_pace]]
        return render_template('comparison.html', data=data)

    @app.route('/routes')
    def routeview():
        data = request.form.get('routes')
        route_trace = []
        if session['time'] and session['distance'] and session['location'] and session['elevation']:
            route_trace = return_valid_routes(session['location'], session['distance'],
                                              session['time'], session['elevation'], session['range'])
        else:
            return redirect(url_for('map'))
        return render_template('routeview.html', routes=route_trace)

    @app.route('/prediction')
    def pace_prediction():
        return render_template('predict_pace.html')

    @app.route('/_get_pace_prediction')
    def get_pace_prediction():
        distance = request.args.get('distance', 1000, type=int)
        elevation = request.args.get('elevation', 100, type=int)
        pace = predict_pace(session['code'], distance, elevation)
        return jsonify(pace=pace)

    @app.route('/_get_task_status')
    def get_task_status():
        users = mongo.db.users
        existing_user = users.find_one({'code': session['code']})
        return jsonify(result=existing_user['tasks'])

    @app.route('/_update_task_status')
    def update_task_status():
        users = mongo.db.users
        existing_user = users.find_one({'code': session['code']})
        db.users.update_one({"_id": existing_user['_id']},
                            {"$set": { "tasks": "NOT STARTED"}})
        return '', 204

    return app
