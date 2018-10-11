import hashlib


def hash_md5(unhashed_password):
    hash_object = hashlib.md5(unhashed_password.encode())
    return hash_object.hexdigest()

