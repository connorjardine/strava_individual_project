from stravalib import *


def get_activity(token):
    client = Client(token)
    types = ['time', 'latlng', 'altitude', 'heartrate', 'temp', ]
    all_activities = client.get_activities()
    for i in all_activities:
        print(i.elapsed_time)
        print(i.start_latlng)
        if i.id is not None:
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







