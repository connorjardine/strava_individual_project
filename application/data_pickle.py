import jsonpickle


class Pickle(object):
    def __init__(self, name):
        self.name = name



def freeze(obj):
    return jsonpickle.encode(obj)


def thaw(obj):
    if obj is not None:
        return jsonpickle.decode(obj)
    return None
