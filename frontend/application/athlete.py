from stravalib import Client
from frontend.application.db import *


def athlete_info():
    user = get_user_by_athlete_id()

    client = Client(user(0))

    #athlete = client.get_athlete()
    # activities = client.get_activities()

    return

