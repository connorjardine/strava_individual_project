import pymongo
import time
import numpy as np
from bson.objectid import ObjectId
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from .services import *

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
    mx = np.zeros((h, 5))
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

    np.random.shuffle(data)
    x = data[:, [0, 1, 2, 3]]
    y = data[:, [4]]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1)

    regression_model = LinearRegression()
    regression_model.fit(x_train, y_train)
    #print(regression_model.score(x_test, y_test))
    y_predict = regression_model.predict(x_test)
    regression_model_mse = mean_squared_error(y_predict, y_test)
    #print(math.sqrt(regression_model_mse))
    return str("{0:.2f}".format(regression_model.predict([[distance, distance**2, elevation, elevation**2]])[0][0]))+" km/h"


start_time = time.time()
print(predict_pace("0a932112522523638c0e800f1aecda3c10515371", 10000, 0))
print("--- %s seconds ---" % (time.time() - start_time))
