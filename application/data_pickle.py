import jsonpickle


def freeze(obj):
    return jsonpickle.encode(obj)


def thaw(obj):
    if obj is not None:
        return jsonpickle.decode(obj)
    return None
