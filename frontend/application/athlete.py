from stravalib import Client
from frontend.application.db import *


def get_athlete_info():
    user = get_user_by_athlete_id()

    single_user = first_item(user)

    client = Client(get_athlete_id(single_user))

    athlete = client.get_athlete()

    return athlete


def get_athlete_id(athlete):
    return athlete[0]


def get_athlete_activities(athlete_id):
    client = Client(athlete_id)

    activities = client.get_activities()

    return activities


def first_item(user):
    for i in user:
        return i
    return None
