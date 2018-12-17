import pymongo

from frontend.application.athlete import *
from frontend.application.gpx_comparison import *
from frontend.application.pickle import *

DB_NAME = "c_strava"
DB_HOST = "ds127094.mlab.com"
DB_PORT = 27094
DB_USER = "connor"
DB_PASS = "Password1"

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)


def parse_runs(code, after):
    current_runs = []

    current_user = db.users.find({'code': code})[0]
    print(current_user['_id'])

    for i in db.runs.find():
        current_runs += [[i['_id'], thaw(i['trace']).name]]

    new_runs = get_activity(code, after)
    print(len(new_runs))

    for i in new_runs:
        print(i[1])
        if not current_runs:
            print("do none")
            db.runs.insert_one({"trace": freeze(i[1])})
            current_runs = []
            for j in db.runs.find():
                current_runs += [[j['_id'], thaw(j['trace']).name]]
            print(i[0])
            print(current_runs[-1][0])
            db.users.update_one({"_id": current_user['_id']}, {"$set": {"runs": freeze([[i[0], current_runs[-1][0]]])}})
        else:
            print("check with current_runs")
            flag = False
            for k in current_runs:
                match = track_match(k[1], i[1])
                print("Current runs: " + str(len(current_runs)))
                print(match)
                if match > 80:
                    print("there was a match")
                    current_user = db.users.find({'code': code})[0]
                    update_run = thaw(current_user['runs']).name + [[i[0], k[0]]]
                    db.users.update_one({"_id": current_user['_id']},
                                        {"$set": {"runs": freeze(update_run)}})
                    flag = True
                    break
            if not flag:
                print("No match with current runs")
                db.runs.insert_one({"trace": freeze(i[1])})
                current_runs = []
                for j in db.runs.find():
                    current_runs += [[j['_id'], thaw(j['trace']).name]]
                current_user = db.users.find({'code': code})[0]
                update_run = thaw(current_user['runs']).name + [[i[0], current_runs[-1][0]]]
                db.users.update_one({"_id": current_user['_id']}, {"$set": {"runs": freeze(update_run)}})


parse_runs("0a932112522523638c0e800f1aecda3c10515371", "2016-11-16T00:00:00Z")

