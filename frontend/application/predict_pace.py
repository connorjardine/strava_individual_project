import pymongo
import time
import numpy as np
from bson.objectid import ObjectId

from sklearn.model_selection import train_test_split
from frontend.application.services import *

DB_NAME = "c_strava"
DB_HOST = "ds127094.mlab.com"
DB_PORT = 27094
DB_USER = "connor"
DB_PASS = "Password1"

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)


def generate_data(code):
    current_user = db.users.find({'code': code})[0]
    user_runs = thaw(current_user['runs']).name
    h = sum(len(u['times']) for u in user_runs)
    mx = np.zeros((h, 4))
    it = 0
    for i in user_runs:
        run = list(db.runs.find({'_id': ObjectId(i['id'])}))
        for j in i['times']:
            seconds = convert_seconds(j)
            pace = "{0:.2f}".format(run[0]['distance'] / seconds)
            mx[it] = [pace, seconds, run[0]['distance'], run[0]['elevation']]
            it += 1
    return mx




