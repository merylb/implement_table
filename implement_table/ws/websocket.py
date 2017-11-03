import ujson

from jwt import DecodeError, ExpiredSignatureError
from rest_framework_jwt.utils import jwt_decode_handler
from ws4py.websocket import WebSocket

from  implement_table.ws.messages import WsMessage, WsMessageType, WsError, WsFile
from  implement_table.ws.models import Topic, Subscriber


class MnWebSocket(Subscriber, WebSocket):
    topics = set()
    subscribers = set()

    def opened(self):
        print('test--------------------')

        MnWebSocket.subscribers.add(self)

    def received_message(self, message):
        print('test-------------bbfghgjn-------', message)
        MnWebSocket.handle(self, message.data)

    def closed(self, *args):
        MnWebSocket.connection_closed(self)

    @classmethod
    def handle(cls, web_socket, message):
        msg = WsMessage(**ujson.loads(message))
        msg.subscriber_conn = web_socket

        if msg.type == WsMessageType.authentication.value:
            cls.authentication(msg)
        else:
            topic = cls.get_topic_or_instantiate(msg.topic)
            msg.topic_obj = topic

            if msg.type == WsMessageType.call.value:
                cls.call(msg)
            elif msg.type == WsMessageType.subscribe.value:
                cls.subscribe(msg)
            elif msg.type == WsMessageType.unsubscribe.value:
                cls.unsubscribe(msg)
            elif msg.type == WsMessageType.publish.value:
                cls.publish(msg)

    @classmethod
    def check_response(cls, rep_body, rep_msg):
        if isinstance(rep_body, (dict, list, tuple)):
            rep_body = rep_body
        elif isinstance(rep_body, (str, bool, int, float)) or rep_body is None:
            rep_body = {"__content__": rep_body}
        elif isinstance(rep_body, WsError):
            rep_body = rep_body.body
            rep_msg.error = True
        elif isinstance(rep_body, WsFile):
            rep_body = rep_body.get_body()
        else:
            raise Exception('got wrong response body from {} , got a {}'.format(rep_msg.topic, type(rep_body)))

        rep_msg.body = rep_body

        return rep_msg

    @classmethod
    def authentication(cls, msg):
        from implement_table.authentication.models import MnUser

        rep_msg = WsMessage(msg.id, WsMessageType.authentication.value, msg.topic)
        rep_msg.body = ""

        try:
            data = jwt_decode_handler(msg.body)
            msg.subscriber_conn.user = MnUser.objects.get(id=data['user_id'])
        except DecodeError:
            rep_msg.error = True
        except ExpiredSignatureError:
            rep_msg.error = True

        msg.subscriber_conn.send(rep_msg)

    @classmethod
    def call(cls, msg):
        rep_body = msg.topic_obj.get_method(msg.body, msg_id=msg.id, subscriber=msg.subscriber_conn,
                                            topic=msg.topic_obj, origin_msg=msg.__dict__)
        rep_msg = WsMessage(msg.id, WsMessageType.rep_call.value, msg.topic)

        rep_msg = cls.check_response(rep_body, rep_msg)

        msg.subscriber_conn.send(rep_msg)

    @classmethod
    def notify(cls, msg):
        rep_msg = WsMessage(msg.id, WsMessageType.notify.value, msg.topic)

        rep_body = True
        rep_msg = cls.check_response(rep_body, rep_msg)
        msg.subscriber_conn.send(rep_msg)

    @classmethod
    def subscribe(cls, msg):
        msg.topic_obj.add_subscriber(msg.subscriber_conn)
        cls.notify(msg)

    @classmethod
    def unsubscribe(cls, msg):
        msg.topic_obj.remove_subscriber(msg.subscriber_conn)
        cls.notify(msg)

    @classmethod
    def publish(cls, msg):
        rep_body = msg.topic_obj.get_method(msg.body, msg_id=msg.id, subscriber=msg.subscriber_conn,
                                            topic=msg.topic_obj,
                                            origin_msg=msg.__dict__)
        rep_msg = WsMessage(msg.id, WsMessageType.publish.value, msg.topic)
        rep_msg = cls.check_response(rep_body, rep_msg)

        cls.handle_publish(msg, rep_msg)
        cls.notify(msg)

    @classmethod
    def handle_publish(cls, msg, rep_msg):
        if msg.subscriber_conn is not None:
            if msg.send_to:
                msg.topic_obj.dispatch_to(rep_msg, msg.send_to)
            elif msg.exclude:
                if isinstance(msg.exclude, bool):
                    exclude = [msg.subscriber_conn]
                else:
                    exclude = msg.exclude

                msg.topic_obj.broadcast(rep_msg, exclude)
            else:
                msg.topic_obj.broadcast(rep_msg)
        else:
            msg.topic_obj.broadcast(rep_msg)

    @classmethod
    def direct_publish(cls, event, data):
        topic_obj = cls.get_topic_or_instantiate(event)
        rep_msg = WsMessage(None, WsMessageType.publish.value, event, exclude=False)

        rep_body = topic_obj.get_method(data, msg_id=rep_msg.id, subscriber=None,
                                        topic=topic_obj,
                                        origin_msg=dict())
        rep_msg = cls.check_response(rep_body, rep_msg)

        topic_obj.broadcast(rep_msg)

    @classmethod
    def connection_closed(cls, conn):
        cls.subscribers.remove(conn)

    @classmethod
    def get_topic_or_instantiate(cls, name):
        if isinstance(name, bool):
            return False

        try:
            return next(topic for topic in cls.topics if topic.name == name)
        except StopIteration:
            topic = Topic(name)
            cls.topics.add(topic)
            return topic
