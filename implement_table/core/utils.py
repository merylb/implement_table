from random import randint

import time


def get_model_class(path):
    names = path.split('.')
    model = names[-1]
    module_ = "App.{}.serializer".format('.'.join(names[:-1]))
    mod = __import__(module_, fromlist=model)

    try:
        return getattr(mod, model)
    except AttributeError:
        raise AttributeError


def get_class(path):
    names = path.split('.')
    model = names[-1]
    module_ = '.'.join(names[:-1])
    mod = __import__(module_, fromlist=model)

    try:
        return getattr(mod, model)
    except AttributeError as e:
        raise e


def generate_id(key_len=16):
    key = ""
    key_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    while key_len > 0:
        key += key_chars[randint(0, len(key_chars) - 1)]
        key_len -= 1

    return "{}.{}".format(str(round(time.time() * 100000)), key)
