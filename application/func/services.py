from sklearn.metrics import mean_squared_error
from stravalib import Client
from flask import request
import gpxpy.geo
import pymongo
import hashlib
import numpy
from numpy import *
import gpxpy.gpx
import gpxpy.geo
import random
import sys

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from ..data_pickle import *

DB_NAME = "c_strava"
DB_HOST = "ds127094.mlab.com"
DB_PORT = 27094
DB_USER = "connor"
DB_PASS = "Password1"

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)


def hash_md5(unhashed_password):
    hash_object = hashlib.md5(unhashed_password.encode())
    return hash_object.hexdigest()


def convert_seconds(i):
    seconds = 0
    seconds += int(i[0]) * 3600 + int(i[2] + i[3]) * 60 + int(i[5] + i[6])
    return seconds


def convert_hours(i):
    return convert_seconds(i) / 3600


def dist_between_start(current_loc, first_coord, distance):
    return int(gpxpy.geo.distance(current_loc[0], current_loc[1], 0, first_coord[0], first_coord[1], 0)) < distance*1000


def return_valid_routes(current_loc, distance, spec_time, elevation, point_distance, code):
    list_valid_routes = []
    run = list(db.runs.find())
    if current_loc is []:
        for i in run:
            time = int(((i['distance'] / 1000) / predict_pace(int(i['distance']), int(i['elevation']), code)) * 3600)
            if int(distance[0] * 1000) < int(i['distance']) < int(distance[1] * 1000) and \
                    int(spec_time[0] * 60) < time < int(spec_time[1] * 60) and \
                    int(elevation[0]) < int(i['elevation']) < int(elevation[1]):
                if dist_between_start(current_loc, thaw(i['firstcoord']), int(point_distance)):
                    m, s = divmod(time, 60)
                    h, m = divmod(m, 60)
                    output_time = '{:02d}:{:02d}:{:02d}'.format(h, m, s)
                    list_valid_routes.append([i['name'], i['strava_id'], thaw(i['firstcoord']),
                                              i['distance'], i['elevation'], output_time])
            if len(list_valid_routes) == 10:
                return list_valid_routes
        return list_valid_routes
    else:
        for i in run:
            time = int(((i['distance'] / 1000) / predict_pace(int(i['distance']), int(i['elevation']), code)) * 3600)
            if int(distance[0] * 1000) < int(i['distance']) < int(distance[1] * 1000) and \
                    int(spec_time[0] * 60) < time < int(spec_time[1] * 60) and \
                    int(elevation[0]) < int(i['elevation']) < int(elevation[1]):
                    m, s = divmod(time, 60)
                    h, m = divmod(m, 60)
                    output_time = '{:02d}:{:02d}:{:02d}'.format(h, m, s)
                    list_valid_routes.append([i['name'], i['strava_id'], thaw(i['firstcoord']),
                                              i['distance'], i['elevation'], output_time])
            if len(list_valid_routes) == 10:
                return list_valid_routes
        return list_valid_routes


def return_all_routes():
    list_routes = []
    run = list(db.runs.find())
    for i in run:
        list_routes.append([i['name'], i['strava_id'], thaw(i['firstcoord']), i['distance'], i['elevation'],
                            i['time'][0]])
    return list_routes


def strava_auth():
    client = Client()
    url = client.authorization_url(client_id=29157, redirect_uri='http://127.0.0.1:5000/login')
    print(url, file=sys.stderr)
    return url


def get_headers(code):
    if code is not None:
        client = Client()
        access_token = client.exchange_code_for_token(client_id=29157,
                                                      client_secret="494606966cbd300f4e0dc96a2062bfa49ec21fe0",
                                                      code=code)
        return access_token

    return None


def get_profile_info(token):
    client = (Client(token)).get_athlete()
    ath = [client.firstname, client.lastname, client.profile, client.city, client.state, str(client.updated_at),
           client.friend_count, client.athlete_type, client.measurement_preference]
    return ath


def get_activity(token, limit, after="2000-06-06 14:47:03+00:00"):
    client = Client(token)
    output = []
    pace = {"total": 0, "total_count": 0, "4k": 0, "4k_count": 0, "8k": 0, "8k_count": 0,
            "10k": 0, "10k_count": 0, "13k": 0, "13k_count": 0}
    types = ['time', 'latlng', 'altitude', 'heartrate', 'temp', ]
    all_activities = client.get_activities(limit=limit, after=after)
    for i in all_activities:
        if i.id is not None:
            if i.type == 'Run' and str(i.elapsed_time) != "0:00:00":
                streams = client.get_activity_streams(i.id, types=types, resolution='medium')
                if streams is not None:
                    if 'latlng' in streams.keys() and 'altitude' in streams.keys():
                        c_time = convert_hours(str(i.elapsed_time))
                        if c_time != 0 and int(i.distance) != 0:
                            dist = float(i.distance) / 1000
                            pace['total'] += float("{0:.2f}".format(dist / c_time))
                            pace['total_count'] += 1
                            if dist < 4:
                                pace['4k'] += float("{0:.2f}".format(dist / c_time))
                                pace['4k_count'] += 1
                            if 4 < dist < 8:
                                pace['8k'] += float("{0:.2f}".format(dist / c_time))
                                pace['8k_count'] += 1
                            if 8 < dist < 13:
                                pace['10k'] += float("{0:.2f}".format(dist / c_time))
                                pace['10k_count'] += 1
                            else:
                                pace['13k'] += float("{0:.2f}".format(dist / c_time))
                                pace['13k_count'] += 1
                        output.append([i.name, i.distance, i.type, str(i.elapsed_time),
                                       str(int(i.total_elevation_gain)), streams['latlng'].data, i.id, i.description])
                        after = str(i.start_date)
                    else:
                        print("stream exists but no latlng field")
                else:
                    print("stream is none")
            else:
                print("incorrect activity or bogus time")
        else:
            print("upload id is none")

    return [output, pace, after]


def generate_data(code):
    current_user = db.users.find({'code': code})[0]
    user_runs = thaw(current_user['runs'])
    h = int(sum(len(u['times']) for u in user_runs))
    mx = numpy.zeros((h+1, 5))
    it = 0
    runs = list(db.runs.find())
    for i in user_runs:
        for run in runs:
            if run['id'] == i['id'] and it <= h:
                for j in i['times']:
                    if convert_hours(j) != 0.0:
                        pace = convert_seconds(j) / (run['distance'] / 1000)

                        dist = int(run['distance'])
                        elev = int(run['elevation'])
                    else:
                        pace = None
                        dist = None
                        elev = None
                    mx[it] = [dist, dist**2, elev, elev**2, pace]
                    it += 1
    numpy.random.shuffle(mx)
    x = mx[:, [0, 1, 2, 3]]
    y = mx[:, [4]]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1)

    regression_model = LinearRegression()
    return regression_model.fit(x_train, y_train)


def predict_pace(distance, elevation, code):
    current_user = db.users.find({'code': code})[0]
    model = thaw(current_user['pred_data'])
    return model.predict([[distance, distance**2, elevation, elevation**2]])[0][0]


def convert_pace_data(data):
    print(data, file=sys.stderr)
    if data['total_count'] is not 0:
        totalk = "{0:.2f}".format(data['total'] / data['total_count']) + "km/h"
    else:
        totalk = "NA"
    if data['4k_count'] is not 0:
        fivek = "{0:.2f}".format(data['4k'] / data['4k_count']) + "km/h"
    else:
        fivek = "NA"
    if data['8k_count'] is not 0:
        tenk = "{0:.2f}".format(data['8k'] / data['8k_count']) + "km/h"
    else:
        tenk = "NA"
    if data['10k_count'] is not 0:
        tenkup = "{0:.2f}".format(data['10k'] / data['10k_count']) + "km/h"
    else:
        tenkup = "NA"
    if data['13k_count'] is not 0:
        thirk = "{0:.2f}".format(data['13k'] / data['13k_count']) + "km/h"
    else:
        thirk = "NA"
    return [totalk, fivek, tenk, tenkup, thirk]


def merge_dictionaries(current, new):
    return {"total": current['total']+new['total'], "total_count": current['total_count']+new['total_count'],
            "4k": current['4k']+new['4k'], "4k_count": current['4k_count']+new['4k_count'],
            "8k": current['8k']+new['8k'], "8k_count": current['8k_count']+new['8k_count'],
            "10k": current['10k']+new['10k'], "10k_count": current['10k_count']+new['10k_count'],
            "13k": current['13k'] + new['13k'], "13k_count": current['13k_count'] + new['13k_count']}


def get_pop_run(code):
    current_user = db.users.find({'code': code})[0]
    runs = list(thaw(current_user['runs']))
    largest = [0, 0, 0]
    largest_time = [0, 0, 0]
    for i in runs:
        if len(i['times']) >= largest[0]:
            largest[0] = len(i['times'])
            largest_time[0] = i
        elif len(i['times']) >= largest[1]:
            largest[1] = len(i['times'])
            largest_time[1] = i
        elif len(i['times']) >= largest[2]:
            largest[2] = len(i['times'])
            largest_time[2] = i
    return largest_time


def get_run_with_id(user_runs):
    runs = db.runs.find()
    req_runs = []
    print(user_runs, file=sys.stderr)
    for k in user_runs:
        for i in runs:
            if int(i['id']) == int(k['id']):
                req_runs.append([i['name'], i['strava_id'], thaw(i['firstcoord']), i['distance'], i['elevation'],
                                 i['time'][0], len(k['times'])])
    return req_runs


def get_run(id):
    return db.runs.find({"id": id})[0]


def get_random_run(code):
    current_user = db.users.find({'code': code})[0]
    runs = list(thaw(current_user['runs']))
    index = random.randint(0, len(runs))
    return runs[index]


def user_data_check(code):
    current_user = db.users.find({'code': code})[0]
    return current_user['runs'] is not ""


def run_data_check():
    return (db.runs.find()).count() != 0
