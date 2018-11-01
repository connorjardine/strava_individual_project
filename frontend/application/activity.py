from stravalib import *
import arrow
from datetime import datetime


def get_activity(token):
    client = Client(token)
    types = ['time', 'latlng', 'altitude', 'heartrate', 'temp', ]
    all_activities = client.get_activities(limit=100)
    for i in all_activities:
        if i.id is not None:
            print(i.id)
            streams = client.get_activity_streams(i.id, types=types, resolution='medium')

            if streams is not None:
                if 'latlng' in streams.keys():
                    print(streams['latlng'].data)
                else:
                    print("stream exists but no latlng field")
            else:
                print("stream is none")
        else:
            print("upload id is none")


print(get_activity("0a932112522523638c0e800f1aecda3c10515371"))






