import pymongo
import time

from frontend.application.gpx_comparison import *
from frontend.application.services import *

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

    for i in db.runs.find():
        current_runs += [[i['_id'], thaw(i['trace']).name]]

    # This takes 7.8 seconds
    activities = get_activity(code, after)
    new_runs = activities[0]

    current_pace = None
    print(current_pace)
    total_pace = activities[1][0]
    num_pace = activities[1][1]

    if current_pace is None:
        pace = ["{0:.2f}".format(total_pace), num_pace]
    else:
        pace = [(current_pace[0] + "{0:.2f}".format(total_pace)), (current_pace[1] + num_pace)]

    db.users.update_one({"_id": current_user['_id']}, {"$set": {"pace": freeze(pace)}})

    for i in new_runs:
        if not current_runs:
            print("do none")
            db.runs.insert_one({"trace": freeze(i)})
            current_runs = []

            for j in db.runs.find():
                current_runs += [[j['_id'], thaw(j['trace']).name]]
            db.users.update_one({"_id": current_user['_id']}, {"$set": {"runs": freeze([[current_runs[-1][0], [i[3]]]])}})
        else:
            print("Current runs: " + str(len(current_runs)))
            flag = False
            for k in current_runs:

                match = align_tracks(k[1][5][0::8], i[5][0::8], -15)
                print(match)

                if match > 90:
                    print("there was a match")
                    current_user = db.users.find({'code': code})[0]
                    if current_user['runs'] == "":
                        update_run = [[current_runs[-1][0], [i[3]]]]
                    else:
                        update_run = thaw(current_user['runs']).name
                        copy_update_run = update_run
                        for n in copy_update_run:
                            if str(n[0]) == str(k[0]):
                                temp = n
                                update_run.remove(n)
                                temp[1] += [i[3]]
                                update_run += [temp]
                    db.users.update_one({"_id": current_user['_id']},
                                        {"$set": {"runs": freeze(update_run)}})
                    flag = True
                    break
            if not flag:
                print("No match with current runs")
                current_user = db.users.find({'code': code})[0]
                db.runs.insert_one({"trace": freeze(i)})
                current_runs = []
                for j in db.runs.find():
                    current_runs += [[j['_id'], thaw(j['trace']).name]]
                if current_user['runs'] == "":
                    update_run = [[current_runs[-1][0], [i[3]]]]
                else:
                    update_run = thaw(current_user['runs']).name + [[current_runs[-1][0], [i[3]]]]
                db.users.update_one({"_id": current_user['_id']}, {"$set": {"runs": freeze(update_run)}})


print(parse_runs("0a932112522523638c0e800f1aecda3c10515371", "2016-11-16T00:00:00Z"))
