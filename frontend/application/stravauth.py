from stravalib import Client
from flask import request

client = Client()


def strava_auth():
    url = client.authorization_url(client_id=1234, redirect_uri='http://127.0.0.1:5000/authenticate')

    return url

def get_headers():
    return request.headers
