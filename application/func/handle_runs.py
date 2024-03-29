from __future__ import absolute_import

from .gpx_comparison import *
from .services import *
from .celery import run_celery
from ..data_pickle import *

DB_NAME = "c_strava"
DB_HOST = "ds127094.mlab.com"
DB_PORT = 27094
DB_USER = "connor"
DB_PASS = "Password1"

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)


# Filters the number of points in the list to approximately 50 points
def num_filter(x_num):
    return round(x_num/50)


# Calculates the average time of a list of times
def avg_time(time):
    total = 0
    for i in time:
        total += convert_seconds(i)
    return total / len(time)


# Function to parse runs, compares each run with existing runs, inserts new run if unique, appends time to existing run
# If it is not. Updates a user's pace as well as relearns the linear regression model of pace
# Then updates the database
@run_celery.task(name='hr.parse_runs')
def parse_runs(code, limit):
    current_user = db.users.find({'code': code})[0]

    current_runs = list(db.runs.find())
    if current_runs:
        itr = current_runs[-1]['id']
    else:
        itr = -1

    add_new_runs = []

    if current_user['after'] is "":
        activities = get_activity(code, limit)
        new_runs = activities[0]
    else:
        activities = get_activity(code, limit, after=current_user['after'])
        new_runs = activities[0]

    if current_user['runs'] is "" or current_user['runs'] is []:
        user_runs = []
    else:
        user_runs = thaw(current_user['runs'])

    for i in new_runs:
        if not current_runs:
            print("Empty run list")
            itr += 1
            current_runs.append({"id": itr, "name": i[0], "distance": int(i[1]), "type": i[2],
                                      "time": [i[3]], "elevation": i[4], "count": 0, "trace": freeze(i[5]),
                                      "strava_id": i[6], "firstcoord": freeze(i[5][0])})
            add_new_runs.append({"id": itr, "name": i[0], "distance": int(i[1]), "type": i[2],
                                      "time": [i[3]], "elevation": i[4], "count": 0, "trace": freeze(i[5]),
                                      "strava_id": i[6], "firstcoord": freeze(i[5][0])})
            user_runs.append({'id': itr, "times": [i[3]]})
        else:
            print("Current runs: " + str(len(current_runs)))
            flag = False
            for k in current_runs:
                curr_time = avg_time(k['time'])
                new_time = convert_seconds(i[3])
                if (curr_time - 1200) < new_time < (curr_time + 1200):
                    k_trace = thaw(k['trace'])
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
                    k['count'] = k['count'] + 1

                    k['time'] = new_times

                    if user_runs is []:
                        user_runs.append({'id': k['id'], "times": [i[3]]})
                    else:
                        for u in user_runs:
                            if u['id'] == k['id']:
                                u["times"] = new_times
                                break
                    flag = True
                    break
            if not flag:
                print("No match with current runs")
                itr += 1
                current_runs.append({"id": itr, "name": i[0], "distance": int(i[1]), "type": i[2],
                                     "time": [i[3]], "elevation": i[4], "count": 0, "trace": freeze(i[5]),
                                     "strava_id": i[6], "firstcoord": freeze(i[5][0])})
                add_new_runs.append({"id": itr, "name": i[0], "distance": int(i[1]), "type": i[2],
                                     "time": [i[3]], "elevation": i[4], "count": 0, "trace": freeze(i[5]),
                                     "strava_id": i[6], "firstcoord": freeze(i[5][0])})

                user_runs.append({'id': itr, "times": [i[3]]})

    pace_data = generate_data(code)
    if add_new_runs:
        db.runs.insert_many(add_new_runs)
    else:
        db.users.update_one({"_id": current_user['_id']}, {"$set": {"tasks": "COMPLETE",
                                                                    "pred_data": freeze(pace_data)}})
        return 'complete'

    if current_user['pace'] is not "":
        db.users.update_one({"_id": current_user['_id']},
                            {"$set": {"pace": freeze(merge_dictionaries(thaw(current_user['pace']), activities[1]))}})
    else:
        db.users.update_one({"_id": current_user['_id']}, {"$set": {"pace": freeze(activities[1])}})

    db.users.update_one({"_id": current_user['_id']}, {"$set": {"runs": freeze(user_runs),
                                                                "tasks": "COMPLETE", "after": activities[2],
                                                                "pred_data": freeze(pace_data),
                                                                "last_id": add_new_runs[-1]["id"]}})
    return 'complete'
