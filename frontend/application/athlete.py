from stravalib import Client


def athlete_id(token):
    client = Client(token)

    athlete = client.get_athlete()

    return athlete.id


def get_activity(token, recent):
    client = Client(token)
    output = []
    types = ['time', 'latlng', 'altitude', 'heartrate', 'temp', ]
    all_activities = client.get_activities(after=recent)
    for i in all_activities:
        if i.id is not None:
            streams = client.get_activity_streams(i.id, types=types, resolution='medium')

            if streams is not None:
                if 'latlng' in streams.keys():
                    output += [[str(i.elapsed_time), streams['latlng'].data]]
                else:
                    print("stream exists but no latlng field")
            else:
                print("stream is none")
        else:
            print("upload id is none")

    return output


