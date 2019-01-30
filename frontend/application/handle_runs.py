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


def num_filter(x):
    return round(x/50)


def avg_time(time):
    total = 0
    for i in time:
        total += convert_seconds(i)
    return total / len(time)


def parse_runs(code, after, limit):
    current_user = db.users.find({'code': code})[0]

    # This takes 7.8 seconds
    activities = get_activity(code, after, limit)
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

    current_user = db.users.find({'code': code})[0]
    if current_user['runs'] is "":
        user_runs = []
    else:
        user_runs = thaw(current_user['runs']).name

    for i in new_runs:
        current_runs = list(db.runs.find())
        print(len(current_runs))
        if not current_runs:
            print("do none")
            id_ = db.runs.insert_one({"name": i[0], "distance": int(i[1]), "type": i[2],
                                      "time": [i[3]], "elevation": i[4], "trace": freeze(i[5]),
                                      "strava_id": i[6], "firstcood": freeze(i[5][0])})

            user_runs.append({'id': str(id_.inserted_id), "times": [i[3]]})
        else:
            print("Current runs: " + str(len(current_runs)))
            flag = False
            for k in current_runs:
                curr_time = avg_time(k['time'])
                new_time = convert_seconds(i[3])
                if (curr_time - 1200) < new_time < (curr_time + 1200):
                    k_trace = thaw(k['trace']).name
                    if len(k_trace) > 50:
                        k_filter = num_filter(len(k_trace))
                    else:
                        k_filter = 1
                    if len(i[5]) > 50:
                        i_filter = num_filter(len(i[5]))
                    else:
                        i_filter = 1
                    match = align_tracks(k_trace[0::k_filter], i[5][0::i_filter], -15)
                else:
                    match = 0
                if match > 90:
                    print("there was a match")
                    new_times = k['time'] + [i[3]]

                    db.runs.update_one({"_id": k['_id']},
                                        {"$set": {"time": new_times}})

                    if user_runs is []:
                        user_runs.append({'id': str(k['_id']), "times": [i[3]]})
                    else:
                        for u in user_runs:
                            if u['id'] == str(k['_id']):
                                new_times = u['times'] + [i[3]]
                                temp_u = {'id': str(k['_id']), "times": new_times}
                                user_runs.remove(u)
                                user_runs.append(temp_u)
                                break
                    flag = True
                    break
            if not flag:
                print("No match with current runs")
                current_user = db.users.find({'code': code})[0]
                id_ = db.runs.insert_one({"name": i[0], "distance": int(i[1]), "type": i[2],
                                          "time": [i[3]], "elevation": i[4], "trace": freeze(i[5]),
                                          "strava_id": i[6], "firstcood": freeze(i[5][0])})

                user_runs.append({'id': str(id_.inserted_id), "times": [i[3]]})
    db.users.update_one({"_id": current_user['_id']}, {"$set": {"runs": freeze(user_runs)}})


start_time = time.time()
print(parse_runs("0a932112522523638c0e800f1aecda3c10515371", "2016-11-16T00:00:00Z", 400))
print("--- %s seconds ---" % (time.time() - start_time))
