import hashlib
from frontend.application.db import *


def hash_md5(unhashed_password):
    hash_object = hashlib.md5(unhashed_password.encode())
    return hash_object.hexdigest()


def authorise_login(username, password):
    user = get_user_by_username(username)
    print(user[4])
    if str(user[4]) == str(username) and str(user[5]) == str(password):
        return True
    return False

