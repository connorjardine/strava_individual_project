from __future__ import absolute_import
from collections import Counter

from .gpx_comparison import *
from .services import *
from .celery import run_celery
from .pickle import *

DB_NAME = "c_strava"
DB_HOST = "ds127094.mlab.com"
DB_PORT = 27094
DB_USER = "connor"
DB_PASS = "Password1"

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)


def num_filter(x_num):
    return round(x_num/50)


def avg_time(time):
    total = 0
    for i in time:
        total += convert_seconds(i)
    return total / len(time)


@run_celery.task(name='hr.parse_runs')
def parse_runs(code, limit, after=None):
    current_user = db.users.find({'code': code})[0]

    current_runs = list(db.runs.find())
    if current_runs:
        itr = current_runs[-1]['id']
    else:
        itr = -1

    add_new_runs = []

    # This takes 7.8 seconds
    activities = get_activity(code, limit, after)
    new_runs = activities[0]


    if current_user['pace']:
        current_pace = Counter((thaw(current_user['pace'])).name)
        new_pace = Counter(activities[1])
        db.users.update_one({"_id": current_user['_id']}, {"$set": {"pace": freeze(dict(current_pace + new_pace))}})
    else:
        db.users.update_one({"_id": current_user['_id']}, {"$set": {"pace": freeze(activities[1])}})

    if current_user['runs'] is "":
        user_runs = []
    else:
        user_runs = thaw(current_user['runs']).name

    for i in new_runs:
        if not current_runs:
            print("Empty run list")
            itr += 1
            current_runs.append({"id": itr, "name": i[0], "distance": int(i[1]), "type": i[2],
                                      "time": [i[3]], "elevation": i[4], "trace": freeze(i[5]),
                                      "strava_id": i[6], "firstcoord": freeze(i[5][0])})
            add_new_runs.append({"id": itr, "name": i[0], "distance": int(i[1]), "type": i[2],
                                      "time": [i[3]], "elevation": i[4], "trace": freeze(i[5]),
                                      "strava_id": i[6], "firstcoord": freeze(i[5][0])})
            user_runs.append({'id': itr, "times": [i[3]]})
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
                                     "time": [i[3]], "elevation": i[4], "trace": freeze(i[5]),
                                     "strava_id": i[6], "firstcoord": freeze(i[5][0])})
                add_new_runs.append({"id": itr, "name": i[0], "distance": int(i[1]), "type": i[2],
                                     "time": [i[3]], "elevation": i[4], "trace": freeze(i[5]),
                                     "strava_id": i[6], "firstcoord": freeze(i[5][0])})

                user_runs.append({'id': itr, "times": [i[3]]})
    db.users.update_one({"_id": current_user['_id']}, {"$set": {"runs": freeze(user_runs)}})
    if add_new_runs:
        db.runs.insert_many(add_new_runs)
    return 'complete'


'''
start_time = time.time()
print(parse_runs("0a932112522523638c0e800f1aecda3c10515371", 10, "2016-11-16T00:00:00Z"))
print("--- %s seconds ---" % (time.time() - start_time))
'''