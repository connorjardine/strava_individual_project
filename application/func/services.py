from sklearn.metrics import mean_squared_error
from stravalib import Client
from flask import request
import gpxpy.geo
import pymongo
import hashlib
import numpy
from bson.objectid import ObjectId
from numpy import *
import gpxpy.gpx
import gpxpy.geo
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
    return int(gpxpy.geo.distance(current_loc[0], current_loc[1], 0, first_coord[0], first_coord[1], 0)) < distance


def return_valid_routes(current_loc, distance, spec_time, elevation, point_distance):
    list_valid_routes = []
    run = list(db.runs.find())
    for i in run:
        if int(i['distance']) < int(distance) and convert_seconds(i['time'][0]) < int(spec_time) and \
                int(i['elevation']) < int(elevation):
            if dist_between_start(current_loc, thaw(i['firstcoord'])['name'], int(point_distance)):
                list_valid_routes.append([i['name'], i['strava_id'], thaw(i['firstcoord'])['name'],
                                          i['distance'], i['elevation'], i['time'][0]])

    return list_valid_routes


def strava_auth():
    client = Client()
    url = client.authorization_url(client_id=29157, redirect_uri='http://127.0.0.1:5000/register')

    return url


def get_headers():
    code = request.args.get('code')

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


def get_activity(token, limit, recent=None):
    client = Client(token)
    output = []
    pace = {"5k": 0, "5k_count": 0, "10k": 0, "10k_count": 0, "10kup": 0, "10kup_count": 0}
    types = ['time', 'latlng', 'altitude', 'heartrate', 'temp', ]
    all_activities = client.get_activities(after="2016-11-16T00:00:00Z", limit=limit)
    for i in all_activities:
        if i.id is not None:
            if i.type == 'Run':
                streams = client.get_activity_streams(i.id, types=types, resolution='medium')
                if streams is not None:
                    if 'latlng' in streams.keys() and 'altitude' in streams.keys():
                        c_time = convert_hours(str(i.elapsed_time))
                        if c_time != 0 and int(i.distance) != 0:
                            dist = float(i.distance) / 1000
                            if dist < 5:
                                pace['5k'] += float("{0:.2f}".format(dist / c_time))
                                pace['5k_count'] += 1
                            if 5 < dist < 10:
                                pace['10k'] += float("{0:.2f}".format(dist / c_time))
                                pace['10k_count'] += 1
                            else:
                                pace['10kup'] += float("{0:.2f}".format(dist / c_time))
                                pace['10kup_count'] += 1
                        print(i.start_date, file=sys.stderr)
                        output.append([i.name, i.distance, i.type, str(i.elapsed_time),
                                       str(int(i.total_elevation_gain)), streams['latlng'].data, i.id, i.description])
                    else:
                        print("stream exists but no latlng field")
                else:
                    print("stream is none")
            else:
                print("incorrect activity")
        else:
            print("upload id is none")
    return [output, pace]


def generate_data(code):
    current_user = db.users.find({'code': code})[0]
    user_runs = thaw(current_user['runs'])['name']
    h = sum(len(u['times']) for u in user_runs)
    mx = numpy.zeros((h, 5))
    it = 0
    runs = list(db.runs.find())
    for i in user_runs:
        for run in runs:
            if run['id'] == i['id']:
                for j in i['times']:
                    pace = (run['distance'] / 1000) / convert_hours(j)
                    dist = int(run['distance'])
                    elev = int(run['elevation'])
                    mx[it] = [dist, dist**2, elev, elev**2, pace]
                    it += 1
    return mx


def predict_pace(code, distance, elevation):
    data = generate_data(code)

    numpy.random.shuffle(data)
    x = data[:, [0, 1, 2, 3]]
    y = data[:, [4]]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1)

    regression_model = LinearRegression()
    regression_model.fit(x_train, y_train)
    #print(regression_model.score(x_test, y_test))
    y_predict = regression_model.predict(x_test)
    #regression_model_mse = mean_squared_error(y_predict, y_test)
    #print(math.sqrt(regression_model_mse))
    return "Your predicted pace is: "+str("{0:.2f}".format(regression_model.predict([[distance, distance**2, elevation, elevation**2]])[0][0]))+" km/h"


'''
start_time = time.time()
print(predict_pace("0a932112522523638c0e800f1aecda3c10515371", 100, 0))
print("--- %s seconds ---" % (time.time() - start_time))
'''



