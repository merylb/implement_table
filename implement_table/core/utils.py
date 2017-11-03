import re
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


class FullName:
    @property
    def full_name(self):
        name = ' '.join([getattr(self.title, 'value', ''), self.last_name, self.first_name])
        return re.sub('^ ', '', name)

    def dcm_full_name(self):
        return "^".join([self.last_name, self.first_name])


class ModuleModel:
    @property
    def _model(self):
        return self.__class__.__name__

    @property
    def track_by(self):
        return '{}-{}'.format(self.__class__.__name__, self.id)

    @property
    def _module(self):
        return self.__class__.__module__
