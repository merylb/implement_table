import ujson
import traceback
from base64 import b64encode
from enum import Enum

from  implement_table.core.utils import generate_id
from implement_table.ws.exceptions import WsException


class WsMessageType(Enum):
    authentication = 0
    call = 1
    rep_call = 2
    subscribe = 3
    unsubscribe = 4
    publish = 5
    notify = 6


class WsMessage:
    id = None
    type = None
    topic = None
    body = None
    error = None
    exclude = None
    send_to = None
    topic_obj = None
    subscriber_conn = None

    def __init__(self, id, type, topic=None, body="", auth=None, error=False, exclude=True, send_to=[]):
        self.id = id
        self.type = type
        self.topic = topic
        self.subscriber = None
        self.auth = auth
        self.body = body
        self.error = error
        self.exclude = exclude
        self.send_to = send_to

        if self.id is None:
            self.id = generate_id()

    def __repr__(self):
        return ujson.dumps(self.__dict__)


class WsFile():
    name = None
    body = None
    mime = None

    def __init__(self, name="", body=bytes(), mime="application/stream"):
        self.name = name
        self.body = body
        self.mime = mime

    def get_body(self):
        return {"__body__": "data:{};base64,{}".format(self.mime, b64encode(self.body).decode("utf-8")),
                "__b64__": True, "__file__": True, "__name__": self.name}


class WsError:
    body = None

    def __init__(self, body=None, exception=False):
        if isinstance(body, WsException):
            self.body = {"__content__": str(body), "__exception__": exception}
        elif isinstance(body, BaseException):
            self.body = {"__content__": traceback.format_exc(), "__exception__": exception}
        elif isinstance(body, dict) or isinstance(body, list):
            self.body = body
        elif isinstance(body, str) or isinstance(body, bool):
            self.body = {"__content__": body, "__exception__": exception}
        else:
            self.body = {"__error__": True}
