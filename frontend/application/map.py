import gpxpy.geo
import pymongo

from frontend.application.pickle import *

DB_NAME = "c_strava"
DB_HOST = "ds127094.mlab.com"
DB_PORT = 27094
DB_USER = "connor"
DB_PASS = "Password1"

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)


def return_times(oid):
    times = []
    for i in db.users.find():
        if i['runs'] is not "":
            for j in thaw(i['runs']).name:
                if str(j[1]) == str(oid):
                    times += [[j[0]]]
    return times


def return_valid_routes(current_loc, distance):
    list_valid_routes = []

    for i in db.runs.find():
        first_coord = thaw(i['trace']).name[0]
        if int(gpxpy.geo.distance(current_loc[0], current_loc[1], 0, first_coord[0], first_coord[1], 0)) < distance:
            if return_times(i['_id']):
                list_valid_routes += [[i['_id'], return_times(i['_id']), thaw(i['trace']).name]]
    return list_valid_routes

