from stravalib import Client
from flask import request

CLIENT_ID = 29157
CLIENT_SECRET = "494606966cbd300f4e0dc96a2062bfa49ec21fe0"
client = Client()


def strava_auth():
    url = client.authorization_url(client_id=CLIENT_ID, redirect_uri='http://127.0.0.1:5000/authenticate')

    return url


def get_headers():
    return request.args.get('code')


def get_access_token(code):
    if code is not None:
        #access_token = client.exchange_code_for_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=code)

        return [CLIENT_ID, CLIENT_SECRET, code]

    return None


def get_athlete(token):
    if token is not None:
        return token
    return None
