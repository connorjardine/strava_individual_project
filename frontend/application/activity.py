from stravalib import *

client = Client("9e84f96fc0b2af88b6d026161a6836a21b07f0c7")

out = client.get_activities(limit=10)
for item in out:
    print(item + " vvdvds")

