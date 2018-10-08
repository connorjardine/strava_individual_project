from stravalib import Client
from flask import request

from frontend.application.db import insert_user

CLIENT_ID = 29157
CLIENT_SECRET = "494606966cbd300f4e0dc96a2062bfa49ec21fe0"


def strava_auth():
    client = Client()
    url = client.authorization_url(client_id=29157, redirect_uri='http://127.0.0.1:5000/authenticate')

    return url


def get_headers():
    code = request.args.get('code')

    if code is not None:
        client = Client()
        access_token = client.exchange_code_for_token(client_id=29157,
                                                      client_secret="494606966cbd300f4e0dc96a2062bfa49ec21fe0",
                                                      code=code)
        client = Client(access_token)

        client.get_athlete()

        return insert_user(access_token,
                           client.get_athlete().id,
                           client.get_athlete().firstname,
                           client.get_athlete().lastname)
    return "Click on the URL to authorise with Strava."
