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

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        code = request.args.get('code')
        print(code, file=sys.stderr)

        if form.validate_on_submit():
            username = form.username.data
            password = hash_md5(form.password.data)
            users = mongo.db.users
            existing_user = users.find_one({'username': username, 'password': password})
            if existing_user is not None:
                if code is not None:
                    session['code'] = get_headers(code)
                    db.users.update_one({"_id": existing_user['_id']}, {"$set": {"code": "session['code"}})
                session['username'] = username
                session['code'] = existing_user['code']
                session['profile'] = get_profile_info(existing_user['code'])
                db.users.update_one({"_id": existing_user['_id']}, {"$set": {"tasks": "RUNNING"}})
                parse_runs.delay(session['code'], 450)
                return redirect(url_for('profile'))

        return render_template('login.html', form=form)

    # Authentication page for connecting to Strava
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            username = form.username.data
            password = hash_md5(form.password.data)

            users = mongo.db.users
            existing_user = users.find_one({'username': username, 'password': password})
            if existing_user is None:
                users.insert({'code': "", 'username': username, 'password': password, "tasks": "NOT STARTED", "pace": "",
                              "after": ""})
                return redirect(strava_auth())

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
        if user_data_check(code):
            users = mongo.db.users
            existing_user = users.find_one({'code': session['code']})

            user_pop_run = get_pop_run(code)
            pop = get_run_with_id(user_pop_run)
            latest = get_run_with_id([get_random_run(code)])

            user_data = [existing_user['after'][0:19], thaw(existing_user['pace'])['total_count'],
                         len(thaw(existing_user['runs']))]

            return render_template('profile.html', username=username,  profile=profile, pop_run=pop, rand_run=latest,
                                   user_data=user_data)
        return redirect(url_for('no_data'))

    @app.route('/error', methods=['GET', 'POST'])
    def no_data():
        return render_template('no_data.html')

    @app.route('/comparison', methods=['GET', 'POST'])
    def comparison():
        if user_data_check(session['code']):
            users = mongo.db.users.find()
            data = []
            for i in users:
                if i['pace'] is not "":
                    avg_pace = convert_pace_data(thaw(i['pace']))
                    data += [[i['username'], avg_pace]]
            return render_template('comparison.html', data=data)
        return redirect(url_for('no_data'))

    @app.route('/routes')
    def routeview():
        if user_data_check(session['code']):
            return render_template('routeview.html', routes=return_all_routes())
        return redirect(url_for('no_data'))

    @app.route('/_get_routes')
    def get_routes():
        distance = [request.args.get('distance_min', 1000, type=int), request.args.get('distance_max', 1000, type=int)]
        elevation = [request.args.get('elevation_min', 100, type=int), request.args.get('elevation_max', 100, type=int)]
        range = request.args.get('rang_max', 100, type=int)
        time = [request.args.get('time_min', 100, type=int), request.args.get('time_max', 100, type=int)]
        latlng = [float(request.args.get('lat')), float(request.args.get('lon'))]
        routes = return_valid_routes(latlng, distance, time, elevation, range, session['code'])
        print("here", file=sys.stderr)
        if routes:
            return jsonify(new_routes=routes)
        return jsonify(new_routes="No valid runs.")

    @app.route('/prediction')
    def pace_prediction():
        if user_data_check(session['code']):
            table_data =[]
            if user_data_check(session['code']):
                distances_km = [["5k", 5000], ["10k", 10000], ["25k", 25000], ["50k", 50000], ["10mi", 16100],
                                ["1/2 Marathon", 21100], ["Marathon", 42200]]
                for k in distances_km:
                    pace = predict_pace(k[1], 0, session['code'])
                    print(pace, file=sys.stderr)
                    m, s = divmod(int(pace), 60)
                    if m < 0:
                        output_pace = "NA"
                        output_time = "NA"
                    else:
                        output_pace = '{:02d}:{:02d}'.format(int(m), int(s)) + " /km"
                        time = int((k[1] / 1000) * pace)
                        print(time, file=sys.stderr)
                        m, s = divmod(time, 60)
                        h, m = divmod(m, 60)
                        output_time = '{:02d}:{:02d}:{:02d}'.format(h, m, s)

                    table_data.append([k[0], output_pace, output_time])
                return render_template('predict_pace.html', table_data=table_data)
        else:
            return redirect(url_for('no_data'))

    @app.route('/_get_pace_prediction')
    def get_pace_prediction():
        distance = request.args.get('distance', 1000, type=int)
        elevation = request.args.get('elevation', 100, type=int)

        print(distance, elevation, file=sys.stderr)

        pace = predict_pace(distance, elevation, session['code'])
        m, s = divmod(int(pace), 60)
        output_time = '{:02d}:{:02d}'.format(int(m), int(s))
        pace = output_time + " /km"

        print(pace, file=sys.stderr)
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
