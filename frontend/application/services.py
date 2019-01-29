from bson import ObjectId
from stravalib import Client
from flask import request
import gpxpy.geo
import pymongo
import hashlib
import datetime
import time
from numpy import *
import gpxpy.gpx
import gpxpy.geo
import sys

from frontend.application.pickle import *

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
    seconds += int(i[0]) * 3600 + int(i[2] + i[3])*60 + int(i[5] + i[6])
    return seconds


def return_times(oid):
    times = []
    for i in db.users.find():
        if i['runs'] is not "":
            for j in thaw(i['runs']).name:
                if str(j[0]) == str(oid):
                    times += j[1]
    if times:
        return min(times)
    return times


def dist_between_start(current_loc, first_coord, distance):
    return int(gpxpy.geo.distance(current_loc[0], current_loc[1], 0, first_coord[0], first_coord[1], 0)) < distance


def return_valid_routes(current_loc, distance, spec_time, elevation, point_distance):
    list_valid_routes = []
    run = list(db.runs.find())
    for i in run:
        if int(i['distance']) < int(distance) and convert_seconds(i['time'][0]) < int(spec_time) and \
                int(i['elevation']) < int(elevation):
            if dist_between_start(current_loc, thaw(i['firstcood']).name, int(point_distance)):
                list_valid_routes.append([i['name'], i['strava_id'], thaw(i['firstcood']).name,
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


def convert_gpx(gpx_list):
    list_dict = []
    for i in gpx_list:
        list_dict += [{'lat': i[0], 'lon': i[1]}]
    return list_dict


def athlete_id(token):
    client = Client(token)

    athlete = client.get_athlete()

    return athlete.id


def altitude_gain(alt):
    alt_total = 0
    previous = int(alt[0])
    for i in range(len(alt)):
        if int(alt[i]) >= previous:
            alt_total += alt[i] - previous
        previous = alt[i]
    return alt_total


def get_activity(token, recent):
    client = Client(token)
    output = []
    pace = []
    total_pace = 0
    total_num = 0
    types = ['time', 'latlng', 'altitude', 'heartrate', 'temp', ]
    all_activities = client.get_activities(after=recent, limit=400)
    for i in all_activities:
        if i.id is not None:
            if i.type == 'Run':
                streams = client.get_activity_streams(i.id, types=types, resolution='medium')
                if streams is not None:
                    if 'latlng' in streams.keys() and 'altitude' in streams.keys():
                        total_pace += float("{0:.2f}".format(float(i.distance) / convert_seconds(str(i.elapsed_time))))
                        total_num += 1
                        output.append([i.name, i.distance, i.type, str(i.elapsed_time),
                                    str(int(i.total_elevation_gain)), streams['latlng'].data, i.id])
                    else:
                        print("stream exists but no latlng field")
                else:
                    print("stream is none")
            else:
                print("incorrect activity")
        else:
            print("upload id is none")
    pace = [total_pace, total_num]
    return [output, pace]
