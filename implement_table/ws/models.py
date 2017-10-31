import copy

from implement_table.ws.exceptions import WsEventSetNotFound, WsEventSetEventNotFound
from implement_table.ws.messages import WsError


class Subscriber:
    _user = None
    staff = None
    subscriptions = set()

    def __init__(self, *args, **kwargs):
        self.id = id(self)
        super(Subscriber, self).__init__(*args, **kwargs)

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

        # if not self._user.profile.is_root:
        #     from App.shared.staff.models import Staff
        #
        #     self.staff = Staff.objects.get(user=value)

    def add_subscription(self, subscription):
        self.subscriptions.add(subscription)

    def remove_subscription(self, subscription):
        try:
            self.subscriptions.remove(subscription)
        except KeyError:
            pass

    def send(self, msg):
        # self.client_terminated, self.server_terminated
        super(Subscriber, self).send(repr(msg))

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id


class Topic:
    def __init__(self, name):
        self.name = name
        self.subscribers = set()

    def get_method(self, body, **kwargs):
        names = self.name.split('.')
        module = "App." + names[0] + ".events"
        mod = __import__(module, fromlist=names[1] + "Events")

        try:
            return self.dispatch(names, mod, body, **kwargs)
        except Exception as exc:
            return WsError(body=exc, exception=True)

    @property
    def subscribers_set(self):
        return copy.copy(self.subscribers)

    @staticmethod
    def dispatch(names, mod, body, **kwargs):
        try:
            cls = getattr(mod, names[1] + "Events")
            try:
                new_instance = cls()
                method = getattr(new_instance, names[2])

            except AttributeError:
                raise WsEventSetEventNotFound(names[2], names[1], mod)
        except AttributeError:
            raise WsEventSetNotFound(names[1], mod)
        else:
            return new_instance.dispatch(method, body, **kwargs)

    def add_subscriber(self, subscriber):
        self.subscribers.add(subscriber)
        subscriber.add_subscription(self)

    def remove_subscriber(self, subscriber, remove_subscription=True):
        try:
            self.subscribers.remove(subscriber)
            if remove_subscription:
                subscriber.remove_subscription(self)
        except KeyError:
            pass

    def dispatch_to(self, rep_msg, send_to):
        for subscriber in self.subscribers_set:
            if subscriber.id in send_to:
                self.send(subscriber, rep_msg)

    def broadcast(self, rep_msg, exclude=False):
        if exclude:
            for subscriber in self.subscribers_set:
                if subscriber not in exclude:
                    self.send(subscriber, rep_msg)
        else:
            for subscriber in self.subscribers_set:
                self.send(subscriber, rep_msg)

    def send(self, subscriber, msg):
        if subscriber.client_terminated:
            self.remove_subscriber(subscriber)
        else:
            subscriber.send(msg)

    def __eq__(self, o):
        return self.name == o.name and id(self) == id(o)

    def __hash__(self):
        return id(self)
