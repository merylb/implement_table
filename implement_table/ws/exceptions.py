class WsException(Exception):
    pass


class WsObjectNotFound(WsException):
    pk = None


class WsEventNotAllowed(WsException):
    event_name = None


class WsEventSetNotFound(WsException):
    def __init__(self, event_set_name, module):
        message = "The EventSet \"{0}\" not found. [{1}:{0}Events]".format(event_set_name, module.__name__)

        super(WsEventSetNotFound, self).__init__(message)


class WsEventSetEventNotFound(WsException):
    def __init__(self, event_name, event_set_name, module):
        message = "The Event \"{0}\" not found in the EventSet \"{1}\". [{2}:{1}Events.{0}]" \
            .format(event_name, event_set_name, module.__name__)

        super(WsEventSetEventNotFound, self).__init__(message)
